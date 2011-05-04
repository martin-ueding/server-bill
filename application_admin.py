from camelot.view.art import Icon
from camelot.admin.application_admin import ApplicationAdmin
from camelot.admin.section import Section


from gettext import gettext

class MyApplicationAdmin(ApplicationAdmin):
  
	def get_sections(self):
		from camelot.model.memento import Memento
		from camelot.model.authentication import Person, Organization
		from camelot.model.i18n import Translation

		from model import Customer, Package, HosterBill
		return [Section(gettext('data'),
						Icon('tango/22x22/apps/system-users.png'),
						items = [Customer, Package, HosterBill]),
				Section('configuration',
						Icon('tango/22x22/categories/preferences-system.png'),
						items = [Memento, Translation])
				]
