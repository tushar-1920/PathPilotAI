from backend.services.company_salary_dataset import TOP_COMPANIES


TOP_COMPANIES = {

"Netflix":2.1,
"Meta":2.0,
"Stripe":2.0,
"Google":1.9,
"Microsoft":1.85,
"Apple":1.85,
"Amazon":1.75,
"Nvidia":1.8,
"Airbnb":1.85,
"LinkedIn":1.8,
"Uber":1.75,
"Tesla":1.7,
"Adobe":1.7,
"Salesforce":1.7,
"Oracle":1.6,
"IBM":1.5,
"Cisco":1.55,
"Intel":1.55,
"SAP":1.5,
"Qualcomm":1.6

}


COUNTRY_MULTIPLIER = {

"India":1,
"USA":2.2,
"Canada":1.8,
"United Kingdom":1.6,
"Germany":1.6,
"Singapore":1.7,
"Australia":1.7,
"Netherlands":1.6,
"Sweden":1.6,
"Switzerland":2.0

}


class CompanySalaryEngine:

    def company_comparison(self, base_salary, country="USA"):

        multiplier = COUNTRY_MULTIPLIER.get(country,1)

        companies = []

        for company,factor in TOP_COMPANIES.items():

            salary = int(base_salary * factor * multiplier)

            companies.append({

                "company":company,
                "salary":salary

            })

        companies = sorted(companies,key=lambda x:x["salary"],reverse=True)

        return companies