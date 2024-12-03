from datetime import datetime

## This class is responsible for date formating.
class DateFormatter:
    def convert(self, date_str):
        try:
            date_obj = datetime.strptime(date_str, "%Y%m%d")
            return date_obj.strftime("%d-%m-%Y")
        except ValueError:
            return "Invalid Date"
