# WIRE 

## Project Description

WIRE (Weather-Induced Risk Exposure) is a global hazard assessment system which provides both real-time and forecasted risks for institutions with duty of care responsibilities. Unlike generic weather forecasts, WIRE analyses meteorological data with hazards directly in mind and provides actionable intelligence to promote the safety of vulnerable populations, such as the elderly, children, and those injured or unwell. The target users of WIRE include: care homes and nursing facilities, schools and childcare centres, hospitals and A&E departments, local councils and social care organisations. 

The system addresses a gap in the existing weather services. For example, While consumer forecasts may present the information that "it's cold and windy", they don't tell a visiting carer that the conditions pose a particular hypothermia risk for the elderly, or that tomorrow's air quality may pose a risk for asthmatic children during playtime. 
 
While it would be relatively simple and feasible for managers of care institutions to regularly calculate these risk metrics themselves, they are often overburdened by dealing with numerous other operational issues, meaning that something as simple as a "slip/fall risk assessment" can fall through the cracks. By providing a seamless hazard dashboard and forecast, WIRE provides those bearing care responsibilities with a quick, easy and reliable way to be aware of the weather-related hazards present, or arriving, at their location. As well as ensuring a hazard assessment and forecast is always available on demand, WIRE frees up the time care managers to focus on other aspects of their operations, overall providing a better quality of care through consistent risk assessments and more attention spent elsewhere in the organisation. 

WIRE integrates eight hazard modules which assess: 
- Heat stress (NOAA Heat Index methodology)
- Cold exposure (Environment Canada Wind Chill Model)
- Respiratory risk (EPA Air Quality Index standards)
- Slip/fall risk (surface temperature analysis)
- Storm severity (composite weather assessment)
- Local flood risk (precipitation analysis)
- Dehydration risk (geriatric-specific models)
- Travel/visibility safety (transport risk assessment)

Each hazard is scored 1-5 with specific recommendations calibrated for vulnerable groups. The system provides both current conditions and 5-day forecasts with A 3-hour granularity, enabling proactive care planning. Hazard assessments are available globally and are available at a low latency. 

The technical architecture of the system uses Python 3.12 to provide a FastAPI server for the backend, launched stateless and hosted on Vercel. The frontend is written using Next.js with TypeScript and is again hosted (separately) on Vercel. The data is sourced exclusively from OpenWeather via the Current Weather, Forecast and Air Quality APIs.


## Results and Observations

The key achievements of WIRE are: 
- The implementation of eight different hazard assessment modules derived from academic articles and existing methodologies, leveraging the OpenWeather API
- Production-ready, live deployment at https://wire-delta.vercel.app/
- Low-latency response time for hazard calculations 
- A clean, simple and professional UI suitable for institutional decision-makers
- Global coverage (any coordinates are supported by OpenWeather)


The main challenges in this project were: 
- Designing a robust system to provide information to decision makers with minimal friction, including both an intuitive UI (easy navigation, colour coding etc) and a simple hazard scoring system to provide hazard overview without necessitating meteorological detail
- Aligning weather forecast data with air quality forecast data which arrive via separate feeds 
- Calibrating the risk thresholds to vulnerable populations, for example: 8 °C could be considered "mild" for many people but creates cold exposure risk for elderly

The next steps for this project may be: 
- Adding more hazard modules for a wider range of users 
- Allowing customisable/saved hazards and locations to build a personal dashboard rather than having to search each time 
- Proactive notifications/alert systems for particular hazards and thresholds 
- User feedback and product iteration with those directly involved in care settings
- And for sure many other things! 

## Documentation 

Complete documentation is available at
- The README in the GitHub repository: https://github.com/ashleyturner/WIRE
- The methodology section of the live application: https://wire-delta.vercel.app/

The most important parts of the documentation are: 
- The installation instructions, environment variable configuration and project structure overview in README.md
- The docstrings in all python modules and in some functions 
- The user-facing documentation of the hazard calculation references, including links to the relevant publications 

## Social Media Post

I'm excited to present my submission, WIRE, to the OpenWeather Challenge 2025. WIRE transforms weather data into safety assessments for care institutions such as care homes, schools and hospitals. Eight hazard modules are implemented (heat stress, cold exposure, air quality, slip/fall risk...) and scored on a 1-5 scale calibrated for vulnerable populations. It provides real-time and 5-day forecasts, has global coverage and uses open-source frameworks (FastAPI + Next.js). 

Try it: https://wire-delta.vercel.app/
Code: https://github.com/ashleyturner/WIRE