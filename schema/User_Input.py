from pydantic import BaseModel,Field,computed_field,field_validator
from config.city_tiers import tier_1_cities,tier_2_cities
from typing import Literal


class UserInput(BaseModel):

    age : int = Field(...,gt=0,lt=120,description="Age of user.")
    weight : float = Field(...,gt=0,description="Weight of user.")
    height : float = Field(...,gt=0,lt=2.5,description="Weight of user.")
    income_lpa : float = Field(...,gt=0,description="Annual Sallary of user in LPA.")
    smoker: bool = Field(...,description="Are you Smoker or not?")
    city: str = Field(...,description="The City of user.")
    occupation: Literal['retired'
                        , 'freelancer'
                        , 'student'
                        , 'government_job'
                        ,'business_owner'
                        , 'unemployed'
                        , 'private_job'] = Field(...,description="Occupdation of User.")

    @computed_field
    @property
    def bmi(self) -> float :
        return self.weight/(self.height**2)

    @computed_field
    @property
    def lifestyle_risk(self) -> str :
        if self.smoker and self.bmi > 30:
            return "high"
        elif self.smoker or self.bmi > 27:
            return "medium"
        else:
            return "low"

    @computed_field
    @property
    def age_group(self) -> str:
        if self.age < 25:
            return "young"
        elif self.age < 45: 
            return "adult"
        elif self.age < 60:
            return "middle_aged"
        return "senior"

    @computed_field
    @property
    def city_tier(self) -> int:
        if self.city in tier_1_cities:
            return 1
        elif self.city in tier_2_cities:
            return 2
        else:
            return 3

    @field_validator("city")
    def titleCaseNameCheck(cls,value : str) -> str:
        return value.strip().title()
    