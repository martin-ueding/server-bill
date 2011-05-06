import camelot.types
from camelot.model import metadata, Entity, Field, ManyToOne, OneToMany, OneToOne, Unicode, Date, Integer, using_options
from camelot.view.elixir_admin import EntityAdmin
from camelot.view.forms import *


from gettext import gettext

import logging
import datetime


__metadata__ = metadata

class Customer(Entity):
	name = Field(Unicode(200))
	bill_prefix = Field(Unicode(100))
	packages = OneToMany("Package")

	def __repr__(self):
		return gettext("<Customer %s>") % self.name or gettext("unknown Customer")

	def __unicode__(self):
		return self.__repr__()

	class Admin(EntityAdmin):
		verbose_name = gettext("Customer")
		verbose_name_plural = gettext("Customers")

		list_display = ['name', 'bill_prefix', 'packages']

from camelot.admin.object_admin import ObjectAdmin
from camelot.view.controls import delegates

class Package(Entity):
	hoster_customer_number = ManyToOne("HosterCustomerNumber")
	interval_months = Field(Integer)
	customer = ManyToOne("Customer")
	domains = OneToMany("Domain")

	hoster_bills = OneToMany("HosterBill")

	def __init__(self):
		self.due_date = PackageDueDate(self)

	def __repr__(self):
		if self.customer is None:
			display_customer = gettext("unknown Customer")
		else:
			display_customer = self.customer.name

		return gettext("<Package for %s>") % display_customer
	
	def __unicode__(self):
		return self.__repr__()

	@property
	def nextDueDate(self):
		if self.hoster_bills is None:
			logging.warning(gettext("%s has no hoster_bill field") % self.__repr__())
			return None

		if len(self.hoster_bills) <= 0:
			logging.warning(gettext("%s has no hoster_bills") % self.__repr__())
			return None

		last_bill_date = datetime.date(day=1, month=1, year=1)

		for bill in self.hoster_bills:
			if last_bill_date < bill.date:
				last_bill_date = bill.date

		# add the interval to the date
		due_date = datetime.date(day=last_bill_date.day, month=(last_bill_date.month-1+self.interval_months)%12 +1, year=last_bill_date.year + (last_bill_date.month-1+self.interval_months)/12)

		return due_date

	@property
	def aDomain(self):
		if self.domains is None or len(self.domains) == 0:
			return gettext("no domains")

		else:
			return self.domains[0]

	class Admin(EntityAdmin):
		verbose_name = gettext("Package")
		verbose_name_plural = gettext("Packages")

		list_display = ['interval_months', 'customer', 'hoster_customer_number', 'domains', 'aDomain', 'nextDueDate']

class HosterBill(Entity):
	date = Field(Date)
	package = ManyToOne("Package")
	amount = Field(Integer)
	bill_id = Field(Unicode(100))
	payed_date = Field(Date)
	own_bill = OneToOne("OwnBill", inverse='hoster_bill')

	@property
	def isPayed(self):
		return self.amount > 10

	def __repr__(self):
		return gettext("<HosterBill %s>") % self.bill_id or gettext("unknown HosterBill")
	
	def __unicode__(self):
		return self.__repr__()

	class Admin(EntityAdmin):
		verbose_name = gettext("Hoster Bill")
		verbose_name_plural = gettext("Hoster Bills")

		list_display = ['date', 'amount', 'bill_id', 'payed_date', 'package', 'isPayed', 'own_bill']

class HosterCustomerNumber(Entity):
	customer_number = Field(Integer)
	packages = OneToMany("Package")


	def __repr__(self):
		return gettext("<HosterCustomerNumber %s>") % self.customer_number or gettext("unknown HosterCustomerNumber")

	def __unicode__(self):
		return self.__repr__()

	class Admin(EntityAdmin):
		verbose_name = gettext("Hoster Customer Number")
		verbose_name_plural = gettext("Hoster Customer Numbers")

		list_display = ['customer_number', 'packages']


class Domain(Entity):
	url = Field(Unicode)
	package = ManyToOne("Package")

	def __repr__(self):
		return gettext("<Domain %s>") % self.url or gettext("unknown Domain")


	def __unicode__(self):
		return self.__repr__()

	class Admin(EntityAdmin):
		verbose_name = gettext("Domain")
		verbose_name_plural = gettext("Domain")

		list_display = ['url', 'package']


class OwnBill(Entity):
	date = Field(Date)
	amount = Field(Integer)
	hoster_bill = ManyToOne("HosterBill")
	payed_when = Field(Date)
	bill_id = Field(Unicode)

	def __repr__(self):
		return gettext("<OwnBill %s>") % self.bill_id or gettext("unknown OwnBill")

	def __unicode__(self):
		return self.__repr__()

	class Admin(EntityAdmin):
		verbose_name = gettext("Own Bill")
		verbose_name_plural = gettext("Own Bills")

		list_display = ['bill_id', 'date', 'amount', 'payed_when', 'hoster_bill']
