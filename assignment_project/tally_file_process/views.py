from django.http import JsonResponse, HttpResponse
from rest_framework.decorators import api_view
from tally_file_process.services.voucher_service import VoucherService
from tally_file_process.services.excel_generator import ExcelGenerator
import os

@api_view(['POST'])
def generate_voucher_excel(request):
    xml_file_path = request.FILES['file']
    Vch_type = request.POST.get('vch_type')
    
    try:
        # Create VoucherService instance to process the XML file
        voucher_service = VoucherService(xml_file_path)
        vouchers = voucher_service.process_vouchers(Vch_type=Vch_type)

        if not vouchers:
            return JsonResponse({"message": "No vouchers found"}, status=400)

        # Generate Excel using the processed vouchers data
        excel_generator = ExcelGenerator(vouchers)
        excel_generator.generate()

        output_file = os.path.join(os.getcwd(), "vouchers_output.xlsx")
        excel_generator.save(output_file)

        # Return Excel as response
        with open(output_file, "rb") as file:
            response = HttpResponse(file.read(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            response['Content-Disposition'] = f'attachment; filename="vouchers_output.xlsx"'
            return response
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
