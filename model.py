import camelot.types
from camelot.model import metadata, Entity, Field, ManyToOne, OneToMany, Unicode, Date, Integer, using_options
from camelot.view.elixir_admin import EntityAdmin
from camelot.view.forms import *

from elixir.properties import ColumnProperty


from gettext import gettext


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

		list_display = ['name', 'bill_prefix']

class Package(Entity):
	hoster_customer_number = ManyToOne("HosterCustomerNumber")
	interval_months = Field(Integer)
	customer = ManyToOne("Customer")
	domains = OneToMany("Domains")

	hoster_bills = OneToMany("HosterBill")

	def __repr__(self):
		if self.customer is None:
			display_customer = gettext("unknown Customer")
		else:
			display_customer = self.customer.name

		return gettext("<Package for %s>") % display_customer
	
	def __unicode__(self):
		return self.__repr__()

	class Admin(EntityAdmin):
		verbose_name = gettext("Package")
		verbose_name_plural = gettext("Packages")

		list_display = ['interval_months', 'customer']

class HosterBill(Entity):
	date = Field(Date)
	package = ManyToOne("Package")
	amount = Field(Integer)
	bill_id = Field(Unicode(100))
	payed_date = Field(Date)
	own_bill = OneToOne("OwnBill", inverse='hoster_bill')

	@ColumnProperty
	def isPayed(self):
		return self.amount > 10

	def __repr__(self):
		return gettext("<HosterBill %s>") % self.bill_id or gettext("unknown HosterBill")
	
	def __unicode__(self):
		return self.__repr__()

	class Admin(EntityAdmin):
		verbose_name = gettext("Hoster Bill")
		verbose_name_plural = gettext("Hoster Bills")

		list_display = ['date', 'amount', 'bill_id', 'payed_date', 'package', 'isPayed']

class HosterCustomerNumber(Entity):
	customer_number = Field(Integer)
	packages = OneToMany("Packages")


	def __repr__(self):
		return gettext("<HosterCustomerNumber %s>") % self.customer_number or gettext("unknown HosterCustomerNumber")

	def __unicode__(self):
		return self.__repr__()

	class Admin(EntityAdmin):
		verbose_name = gettext("Hoster Customer Number")
		verbose_name_plural = gettext("Hoster Customer Numbers")

		list_display = ['customer_number']


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

		list_display = ['url']


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

		list_display = ['bill_id', 'date', 'payed_when', 'hoster_bill']
