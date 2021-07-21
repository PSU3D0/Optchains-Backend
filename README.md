# Optchains-Backend

This is the backend that powers the optchains API. Built in Django, there are two primary applications, that share a common set of models. The API serves data to the React-powered Optchains frontend. The updater cyclically grabs data from the Yahoo finance API during market hours.

# Two versions

There are two branches to this project:

* Server - Uses Docker and an async task runner to run on an EC2 instance
* Serverless - Uses Zappa and it's scheduling to serve the API and run updates.

The current API is running via Zappa.