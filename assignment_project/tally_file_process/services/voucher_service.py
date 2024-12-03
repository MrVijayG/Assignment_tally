from tally_file_process.utils.date_formatter import DateFormatter
from tally_file_process.utils.xml_parser import XMLParser

## This class is mainly focus on getting all data from the xml file.

class VoucherService:
    def __init__(self, xml_file_path):
        self.xml_file_path = xml_file_path
        self.parser = XMLParser(xml_file_path)
        self.date_formatter = DateFormatter()

    def classify_transaction(self, voucher):
        voucher_type = voucher.find("VOUCHERTYPENAME").text
        if voucher_type in ["Bank", "GST", "TDS - Interest", "IGST"]:
            return "Other"
        
        bill_allocations = voucher.findall(".//BILLALLOCATIONS.LIST")
        if bill_allocations:
            for bill in bill_allocations:
                bill_type = bill.findtext("BILLTYPE", "")
                if bill_type in ["Agst Ref", "New Ref"]:
                    return "Child"
            return "Parent"
        return "Parent"

    def process_vouchers(self,Vch_type="Receipt"):
        root = self.parser.get_root()
        vouchers = []

        for voucher in root.findall(".//VOUCHER"):
            if voucher.find("VOUCHERTYPENAME") is not None and voucher.find("VOUCHERTYPENAME").text == Vch_type:
                transaction_type = self.classify_transaction(voucher)
                vch_type = voucher.attrib.get("VCHTYPE", "Other")
                voucher_number = voucher.findtext("VOUCHERNUMBER", "")
                date = self.date_formatter.convert(voucher.findtext("DATE", ""))
                
                ref_date = (
                    self.date_formatter.convert(voucher.findtext("REFERENCEDATE", ""))
                    if transaction_type == "Child" else "NA"
                )
                if ref_date == "Invalid Date":
                    ref_date = "NA"
                debtor_or_particulars = (
                    voucher.findtext("PARTYLEDGERNAME", "Unknown")
                    if transaction_type == "Parent" else
                    voucher.find(".//ALLLEDGERENTRIES.LIST/LEDGERNAME").text
                )

                amount = sum(
                    float(bill.findtext("AMOUNT", "0")) 
                    for bill in voucher.findall(".//BILLALLOCATIONS.LIST")
                ) if transaction_type == "Parent" else voucher.findtext(".//ALLLEDGERENTRIES.LIST/AMOUNT", "NA")
                
                amount_verified = (
                    "Yes" if transaction_type == "Parent" and 
                    sum(float(bill.findtext("AMOUNT", "0")) for bill in voucher.findall(".//BILLALLOCATIONS.LIST")) == float(amount) 
                    else "No"
                )
                
                for bill in voucher.findall(".//BILLALLOCATIONS.LIST"):
                    name = bill.findtext("NAME", "")
                    bill_type = bill.findtext("BILLTYPE", "")
                    ref_amount = abs(float(bill.findtext("AMOUNT", "0")))
                    
                    if name or bill_type or ref_amount:
                        vouchers.append({
                            "Date": date,
                            "Transaction Type": transaction_type,
                            "Vch No.": voucher_number,
                            "Ref No": name,
                            "Ref Type": bill_type,
                            "Ref Date": ref_date,
                            "Debtor": debtor_or_particulars,
                            "Ref Amount": ref_amount,
                            "Amount": amount,
                            "Particulars": debtor_or_particulars,
                            "Vch Type":vch_type,
                            "Amount Verified": amount_verified
                        })
        return vouchers
