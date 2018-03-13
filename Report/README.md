# PyAR (Python Automation Reporting)
Goal is to have a reporting tool for automate/orchestration products

One scripts to get informations from various source, transform them and
save them in DB
One web app to show results using either table or graph

We should provide:
- yesterday_services: table of top requested services + graph number requested services + error rate
- last_month_errors: table of most frequents error + graph error rate per day
- last_year_errors: table of most frequents error + graph error rate per month
- last_month_users: table of top requesters + graph different user's number per day
- last_year_users: table of top requesters + graph different user's number per month
- last_month_services: table of most requested services + graph number requested services per day
- last_year_services: table of most requested services + graph number requested services per month

We should have a config file:
- authentication: true or false
- ldap_host
- ldap_port
- ldap_user
- ldap_password
- listening port
- listening address


## To Run
Use sample data by removing \_sample in database filename
Or Run one importer script to get real data

```bash
export FLASK_APP=dashboard.py
flask run
```

You should be able to connect to http://127.0.0.1:5000 using admin/admin

You can customize app by changing config.cfg

## ToDo
### v1
- ldap configuration
- one page with average duration per service per month
- beautify login page
### v2
- User can choose to view stats for all Business Unit or choose a BU
- User can choose to view stats for all services or a specific one
- User can favorite at most 4 graphs
- Dashboard showing favorites user's graph
- Available data for services's graph: error rate, average duration, number per day, top 5 most requested
