from npdtools.modules.base import NPDToolsBase
from npdtools.modules.income import NPDToolsIncome
from npdtools.modules.invoice import NPDToolsInvoice


class NPDTools(NPDToolsInvoice, NPDToolsIncome, NPDToolsBase):
    ...
