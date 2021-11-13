# README.md

Takes in the following structure from file

{
  "id": "1234",
  "customer_id": "1234",
  "load_amount": "$123.45",
  "time": "2018-01-01T00:00:00Z"
}

Sorts data to confirm correct ordering and and checks these limits
1. <= 5000 allowed per day
2. <= 20000 allowed per week
3. <= 3 loads per day

Outputs to file
{ "id": "1234", "customer_id": "1234", "accepted": true }


Runs with
> python3 velocity.py