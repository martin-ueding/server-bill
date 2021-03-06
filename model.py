# Copyright (c) 2011 Martin Ueding <dev@martin-ueding.de>

import camelot.types
from camelot.model import metadata, Entity, Field, ManyToOne, OneToMany, OneToOne, Unicode, Date, Integer, using_options
from camelot.view.elixir_admin import EntityAdmin
from camelot.view.forms import *

from gettext import gettext
import logging
import datetime

__metadata__ = metadata


class Customer(Entity):
	"""
	A customer who has multiple packages
	"""

	name = Field(Unicode(200))
	bill_prefix = Field(Unicode(100))
	packages = OneToMany("Package")

	@property
	def all_domains(self):
		# FIXME return a better list
		domains = []
		if self.packages is not None:
			for package in self.packages:
				for domain in package.domains:
					domains.append(domain.__unicode__())

		return domains
				

	def __repr__(self):
		return gettext("<Customer %s>") % self.name or gettext("unknown customer")

	def __unicode__(self):
		return self.name

	class Admin(EntityAdmin):
		verbose_name = gettext("Customer")
		verbose_name_plural = gettext("Customers")

		list_display = ['name', 'bill_prefix', 'packages']


class Package(Entity):
	"""
	A package from the hoster, it contains multiple domains. Each package is
	owned my a certain customer
	"""

	hoster_customer_number = ManyToOne("HosterCustomerNumber")
	interval_months = Field(Integer)
	customer = ManyToOne("Customer")
	domains = OneToMany("Domain")
	hoster_bills = OneToMany("HosterBill")


	@property
	def status(self):
		"""
		returns the status of the package

		This determines the current payment status of the package:
		* whether a new bill is due
		* whether the hoster already send a bill
		* whether this bill is payed by you
		* whether this bill is relayed to the customer
		* whether the relayed bill is payed
		"""

		status_msgs = []
		last_bill = self.getLastBill()
		# fully payed
		if last_bill is not None and not self.needs_payment:
			status_msgs.append(gettext("payed by you"))

		# if there is no last bill
		if last_bill is None:
			status_msgs.append(gettext("cannot determine status"))

		# needs payment but has no bill
		if self.needs_payment:
			status_msgs.append(gettext("hoster bill is due"))

		# unpaid
		if last_bill is not None and not last_bill.is_payed:
			status_msgs.append(gettext("last bill not payed by you"))

		# unrelayed
		if last_bill is not None and not last_bill.is_relayed:
			status_msgs.append(gettext("not relayed to customer"))

			if last_bill.own_bill[0].is_payed:
				status_msgs.append(gettext("payed by customer"))
			else:
				status_msgs.append(gettext("not payed by customer"))

		elif last_bill is not None:
			status_msgs.append(gettext("relayed to customer"))

		return ', '.join(status_msgs)


	@property
	def last_bill_date(self):
		if self.getLastBill() is not None:
			return self.getLastBill().date

		return None


	@property
	def next_due_date(self):
		last_bill_date = self.last_bill_date

		if last_bill_date is None:
			return None
		
		# add the interval to the date
		due_date = datetime.date(day=last_bill_date.day, month=(last_bill_date.month-1+self.interval_months)%12 +1, year=last_bill_date.year + (last_bill_date.month-1+self.interval_months)/12)

		return due_date


	@property
	def needs_payment(self):
		if self.next_due_date is None:
			return False

		return self.next_due_date < datetime.date.today()


	@property
	def a_domain(self):
		if self.domains is None or len(self.domains) == 0:
			return gettext("no domains")

		else:
			return self.domains[0]


	def getLastBill(self):
		if self.hoster_bills is None:
			logging.warning(gettext("%s has no hoster_bill field") % self.__repr__())
			return None

		if len(self.hoster_bills) <= 0:
			logging.warning(gettext("%s has no hoster_bills") % self.__repr__())
			return None

		last_bill = None
		last_bill_date = datetime.date(day=1, month=1, year=1)

		for bill in self.hoster_bills:
			if last_bill_date < bill.date:
				last_bill = bill
				last_bill_date = bill.date

		return last_bill


	def __repr__(self):
		if self.customer is None:
			display_customer = "<%s>" % gettext("unknown customer")
		else:
			display_customer = self.customer.__repr__()

		return gettext("<Package for %s>") % display_customer

	
	def __unicode__(self):
		if self.customer is None:
			display_customer = gettext("unknown customer")
		else:
			display_customer = self.customer.__unicode__()

		return gettext("Package %s of %s") % (self.a_domain, display_customer)


	class Admin(EntityAdmin):
		verbose_name = gettext("Package")
		verbose_name_plural = gettext("Packages")

		list_display = ['interval_months', 'customer', 'hoster_customer_number', 'domains', 'a_domain', 'last_bill_date', 'next_due_date', 'needs_payment', 'status']


class HosterBill(Entity):
	"""
	a bill from the hoster

	These are bills that your webhoster has send you regarding a package you
	have bought for any of your customers.
	"""

	date = Field(Date)
	package = ManyToOne("Package")
	amount = Field(Integer)
	bill_id = Field(Unicode(100))
	payed_date = Field(Date)
	own_bill = OneToMany("OwnBill")


	@property
	def is_payed(self):
		return self.payed_date is not None


	@property
	def is_relayed(self):
		return self.own_bill is not None and len(self.own_bill) > 0


	def __repr__(self):
		return gettext("<HosterBill %s>") % self.bill_id or gettext("unknown hoster bill")
	

	def __unicode__(self):
		return str(self.bill_id) or gettext("unknown HosterBill")


	class Admin(EntityAdmin):
		verbose_name = gettext("Hoster Bill")
		verbose_name_plural = gettext("Hoster Bills")

		list_display = ['date', 'amount', 'bill_id', 'payed_date', 'package', 'is_payed', 'own_bill', 'is_payed', 'is_relayed']


class HosterCustomerNumber(Entity):
	"""
	customer number at the hoster

	This is the customer number that your hoster assigns you. This is handy to
	group several packages together.
	"""

	customer_number = Field(Integer)
	packages = OneToMany("Package")


	def __repr__(self):
		return gettext("<HosterCustomerNumber %s>") % self.customer_number or gettext("unknown hoster customer number")


	def __unicode__(self):
		return str(self.customer_number) or gettext("unknown hoster customer number")


	class Admin(EntityAdmin):
		verbose_name = gettext("Hoster Customer Number")
		verbose_name_plural = gettext("Hoster Customer Numbers")

		list_display = ['customer_number', 'packages']


class Domain(Entity):
	"""
	a internet domain

	This is a domain that is associated with a package. The domains itself do
	not influence the billing process, but they make it easier to connect
	packages to customers.
	"""

	url = Field(Unicode)
	package = ManyToOne("Package")


	@property
	def customer(self):
		if self.package is not None and self.package.customer is not None:
			return self.package.customer.__unicode__()

		return None


	def __repr__(self):
		return gettext("<Domain %s>") % self.url or gettext("unknown domain")


	def __unicode__(self):
		return self.url


	class Admin(EntityAdmin):
		verbose_name = gettext("Domain")
		verbose_name_plural = gettext("Domain")

		list_display = ['url', 'package', 'customer']


class OwnBill(Entity):
	"""
	a bill from you to your customer

	A bill where you relay the costs from the hoster to your customer.
	"""

	date = Field(Date)
	amount = Field(Integer)
	hoster_bill = ManyToOne("HosterBill")
	payed_when = Field(Date)
	bill_id = Field(Unicode)


	@property
	def is_payed(self):
		return self.payed_when is not None


	def __repr__(self):
		return gettext("<OwnBill %s>") % self.bill_id or gettext("unknown own bill")


	def __unicode__(self):
		return self.bill_id


	class Admin(EntityAdmin):
		verbose_name = gettext("Own Bill")
		verbose_name_plural = gettext("Own Bills")

		list_display = ['bill_id', 'date', 'amount', 'payed_when', 'hoster_bill', 'is_payed']

