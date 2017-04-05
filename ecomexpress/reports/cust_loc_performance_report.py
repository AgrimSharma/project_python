

def customer_location_report(request): 
	codes='''92006,11007,22092,88008,81013,69060,41107,80126,12016,34004,13010,96047,80108,96038,94020'''
        today=datetime.datetime.now().date()
	first=datetime.date(datetime.date.today().year, datetime.date.today().month, 1)
        today=today.strftime("%Y-%m-%d")
        first=first.strftime("%Y-%m-%d")
