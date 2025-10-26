# To Do

-   [ ] add self ping function to fastapi lifespan

-   [ ] add tests
    -   watch arjan or someone else to start off
    -   to be done after deploying the application
    -   use pytest for api and db tests
    -   use cursor or copilot
-   [ ] add a tooltip to suggest the user for one to use

# In Progress

-   [ ] how to write tests for api, service, repository layers
-   [ ] when to use fixtures and pytest-mock
-   [ ] add payloads to the conftest
-   [ ] assert json as a whole, not properties individually
-   [ ] write appropriate tests for my controller repo and service layer first for my existing ones
-   [ ] migrate all endpoints to repo and service pattern
-   [ ] replace shadcn with nuxt ui bit by bit
    -   specify steps
-   [ ] play with shap in a notebook

# Done

-   [x] make ml section follow cookie cutter data science structure (manually made)
-   [x] use uv in ml model section
-   [x] use databricks for ml model
-   [x] publish ml as package
-   [x] migrate server to uv
-   [x] deploy client to vercel
-   [x] see if the y column encoder is there
-   [x] fragment the lifespan to separate files
    -   [x] for db file, create separate clear functions
    -   [x] use the new ml model and shap
    -   [x] find a way to recreate the shap values functions
-   [x] remove db inserting logicfrom lifespan
    -   make it simple functions
-   [x] use uploaded models in server
-   [x] deploy server
    -   [x] docker file creation for server
-   [x] update all readmes
