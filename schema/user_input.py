from typing import Literal,Annotated,Optional
from pydantic import BaseModel,computed_field,Field,field_validator

from config.city_tier import tier_1_cities,tier_2_cities


# data====================================================
# tier_1_cities = [
#     "Mumbai",
#     "Delhi",
#     "Bangalore",
#     "Chennai",
#     "Kolkata",
#     "Hyderabad",
#     "Pune"
# ]

# tier_2_cities = [
#     "Jaipur",
#     "Chandigarh",
#     "Indore",
#     "Lucknow",
#     "Patna",
#     "Ranchi",
#     "Visakhapatnam",
#     "Coimbatore",
#     "Bhopal",
#     "Nagpur",
#     "Vadodara",
#     "Surat",
#     "Rajkot",
#     "Jodhpur",
#     "Raipur",
#     "Amritsar",
#     "Varanasi",
#     "Agra",
#     "Dehradun",
#     "Mysore",
#     "Jabalpur",
#     "Guwahati",
#     "Thiruvananthapuram",
#     "Ludhiana",
#     "Allahabad",
#     "Udaipur",
#     "Aurangabad",
#     "Hubli",
#     "Belgaum",
#     "Salem",
#     "Vijayawada",
#     "Tiruchirappalli",
#     "Bhavnagar",
#     "Gwalior",
#     "Dhanbad",
#     "Bareilly",
#     "Aligarh",
#     "Gaya",
#     "Kozhikode",
#     "Warangal",
#     "Kolhapur",
#     "Bilaspur",
#     "Jalandhar",
#     "Noida",
#     "Guntur",
#     "Asansol",
#     "Siliguri"
# ]

#pydantic model to validate data
class UserInput(BaseModel):
    age:Annotated[int,Field(...,gt=0,lt=120,description='Age of User')]
    weight:Annotated[float,Field(...,gt=0,description=' weight of User')]
    height:Annotated[float,Field(...,gt=0,lt=2.5,description=' height  of User')]
    income_lpa:Annotated[float,Field(...,gt=0,description=' Income of User in LPA')]
    smoker:Annotated[bool,Field(...,description='User is smoker or not')]
    city:Annotated[str,Field(...,description=' City of User')]
    occupation: Annotated[
        Literal['retired', 'freelancer', 'student', 'government_job', 'business_owner', 'unemployed', 'private_job'],
        Field(..., description='Occupation of User')
    ]

    @field_validator('city')
    @classmethod
    def normalize_city(cla,v:str)->str:
        v=v.strip().title()# converting city name in title case and removing extra space
        return v

    # we want to create new feature also using existing features
    @computed_field
    @property
    def bmi(self)->float:#function name should be same as name of field or feature
        return self.weight/(self.height**2)

    @computed_field
    @property
    def lifestyle_risk(self)->str:
        if self.smoker and self.bmi>30:
            return "high"
        elif self.smoker or self.bmi>27:
            return "medium"
        else:
            return "low"
        
    @computed_field
    @property
    def age_group(self)->str:
        if self.age<25:
            return "young"
        elif self.age<45:
            return "adult"
        elif self.age<60:
            return "middle_aged"
        return "senior"
    
    @computed_field
    @property
    def city_tier(self)->str:
        if self.city in tier_1_cities:
            return 1
        if self.city in tier_2_cities:
            return 2
        else:
            return 3