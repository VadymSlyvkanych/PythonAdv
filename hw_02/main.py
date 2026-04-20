from pydantic import BaseModel, Field, model_validator, EmailStr


class Address(BaseModel):
    city: str = Field(..., min_length=2)
    street: str = Field(..., min_length=3)
    house_number: int = Field(..., gt=0)


class User(BaseModel):
    name: str = Field(..., min_length=2, pattern=r"^[a-zA-Z]+$")
    age: int = Field(..., ge=0, le=120)
    email: EmailStr
    is_employed: bool
    address: Address

    @model_validator(mode='after')
    def validate_age_and_employment(self) -> 'User':
        if self.is_employed and (self.age < 18 or self.age > 65):
            raise ValueError('If user is employed, age must be between 18 and 65')
        return self


def process_registration(json_string: str) -> str:
    user = User.model_validate_json(json_string)
    return user.model_dump_json(indent=2)


if __name__ == '__main__':
    valid_json = """{
        "name": "JohnDoe",
        "age": 30,
        "email": "john.doe@example.com",
        "is_employed": true,
        "address": {
            "city": "NewYork",
            "street": "5thAvenue",
            "house_number": 123
        }
    }"""

    invalid_json_age = """{
        "name": "JohnDoe",
        "age": 70,
        "email": "john.doe@example.com",
        "is_employed": true,
        "address": {
            "city": "NewYork",
            "street": "5thAvenue",
            "house_number": 123
        }
    }"""

    invalid_json_name = """{
        "name": "John Doe",
        "age": 30,
        "email": "john.doe@example.com",
        "is_employed": true,
        "address": {
            "city": "NewYork",
            "street": "5thAvenue",
            "house_number": 123
        }
    }"""

    success_cases = [
        ("Valid employed user", valid_json),
        ("Unemployed user", """{
            "name": "JaneDoe",
            "age": 70,
            "email": "jane.doe@example.com",
            "is_employed": false,
            "address": {
                "city": "LosAngeles",
                "street": "SunsetBoulevard",
                "house_number": 456
            }
        }"""),
    ]

    failure_cases = [
        ("Employed but age > 65", invalid_json_age),
        ("Name contains spaces", invalid_json_name),
    ]

    print("=== SUCCESS CASES ===")
    for name, json_str in success_cases:
        try:
            result = process_registration(json_str)
            print(f"\n--- {name} ---")
            print(result)
        except Exception as e:
            print(f"\n--- {name} ---")
            print(f"ERROR: {e}")

    print("\n=== FAILURE CASES ===")
    for name, json_str in failure_cases:
        try:
            result = process_registration(json_str)
            print(f"\n--- {name} ---")
            print(result)
        except Exception as e:
            print(f"\n--- {name} ---")
            print(f"EXPECTED ERROR: {e}")
