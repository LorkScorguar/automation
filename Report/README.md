# Report
Goal is to have a reporting tool for automate/orchestration products

One scripts to get informations from various source, transform them and
save them in DB
One web app to show results using either table or graph

We should provide:
- yesterday_services: table of top requested services + graph service's number + error rate
- last_month_errors: table of most frequents error + graph error rate per day
- last_year_errors: table of most frequents error + graph error rate per month
- last_month_users: table of top requesters + graph different user's number per day
- last_year_users: table of top requesters + graph different user's number per month
- last_month_services: table of most requested services + graph number requested services per day
- last_year_services: table of most requested services + graph number requested services per month + graph average duration per service over months
