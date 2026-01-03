import datetime
import pytz

TIMEZONE = pytz.timezone("America/Bahia")

def agora(timezone=TIMEZONE):
    return datetime.datetime.now(tz=timezone)
    
def eh_feriado(data):
    return (data.day == 1 and data.month == 1 or data.day == 21 and data.month == 4 or data.day == 1 and data.month == 5 or data.day == 1 and data.month == 5 or data.day == 7 and data.month == 9 or data.day == 12 and data.month == 10 or data.day == 2 and data.month == 11 or data.day == 15 and data.month == 11 or data.day == 25 and data.month == 12 or data.day == 31 and data.month == 12)

def eh_feriado_b3(data):
    return data.day == 24 and data.month == 12 or data.day == 31 and data.month == 12
   
def eh_feriado_movel(data):
    return data.year == 2026 and (data.day in (16,17) and data.month == 2 or data.day == 3 and data.month == 4 or data.day == 4 and data.month == 6) 
       
def eh_fim_de_semana(data):
    return data.weekday() in (5,6)

def eh_dia_util(data):       
    return not eh_fim_de_semana(data) and not eh_feriado(data) and not eh_feriado_movel(data) and not eh_feriado_b3(data)