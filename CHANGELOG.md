# Changelog

All notable changes to MediLinda are in this file. A tool generates it from the commit history.

## [Unreleased]

### Bug fixes
- **server:** Verify api keys through an internal nuxt route
- **client:** Allow one-letter usernames for migrated users
- **client:** Check the session without the better auth client on the server
- **client:** Run vitest without the generated nuxt tsconfig
- **server:** Require login on every api route
- **server:** Build the dashboard service with its repository
- **server:** Set created_at and updated_at when a row is written
- **server:** Call _predict with the arguments it accepts
- **server:** Restore undoes only the delete it was asked to undo
- **server:** Read adrs without an inpatient number, order assessments stably
- **client:** Make the review queries follow the current assessment
- **client:** Stop cards shrinking to nothing in the page body
- **client:** Say 'Username is required' on an empty login field
- **client:** Use the right component names on the dashboard
- **client:** Send the unfinished Monitoring pages to the dashboard
- **client:** Drop a leftover Label component from the institution form
- **server:** Trust only the signed-in user when saving a review
- **client:** Rebuild the review page on the current api
- **client:** Show the signed-in user's own review on the ADR page
- **server:** Send the medicines in the adr response
- **client:** Make the stopped dots on the medicine timeline visible
- **client:** Rebuild the about page with nuxt ui cards
- **client:** Open the feature rankings on the predicted class
- **client:** Tidy the review table on the adr page
- **client:** Add the missing password field to the signup form
- **client:** Confirm before revoking an api key and show the page's states
- **client:** Shrink the form's section list to a slim bar on narrow screens
- **server:** Open a new database connection for each request on turso
- **server:** Run the model before the first database write
- **ml:** Point the training data path at the top-level medilinda_ml folder
- **server:** Give the float fields of the model input the float64 type
- **server:** Install image dependencies from uv.lock


### Build
- **client:** Add better-auth and libsql dependencies
- **client:** Add better-auth api-key plugin
- **client:** Install with legacy peer deps
- **client:** Add vitest
- **server:** Add sqlalchemy-libsql
- **server:** Stop depending on the medilinda-ml package from PyPI
- **server:** Fix the patterns of the docker ignore file
- **server:** Copy the model store into the image, and drop the MLflow settings
- **server:** Move mlflow to the train group
- **server:** Keep the empty model folder in git
- **server:** Move unused dependencies to the train group
- Add git-cliff to generate the changelog
- Leave the compressed data files out of the server image


### Chores
- **client:** Remove stale authstore comments
- Ignore vercel and env files
- **ml:** Remove the package config of medilinda_ml
- **ml:** Add the MLflow runs of the first tracked training
- **ml:** Remove draft and old notebooks
- **ml:** Strip the saved outputs from the notebooks


### Continuous integration
- **client:** Disable automatic vercel git deployments
- Run client and server tests on pull requests
- Build on pull requests, publish on main, deploy only on request
- Remove the workflow that publishes medilinda-ml to PyPI
- Test the ML code in the same run as the server
- Fail a pull request when the changelog is not current


### Documentation
- Document better auth setup and api keys
- Document the turso app database
- Describe the audit trail and adr history
- **client:** Say the messages follow up with the facility, and thank the university
- Describe the new place of medilinda_ml and how to train
- **ml:** Remove the reference to a missing .env.example file
- Describe the model store, and the train and export commands
- Describe the experiment tracking folder
- Say that the runs folder is in git, and where to run MLflow
- **ml:** Rewrite the EDA notebook for the real dataset
- **client:** Move the credits from Home to About and say this is a fourth-year project
- **client:** State the scope of the project on the About page
- Add a short scope section to the README
- **client:** State the data and its limits on the About page
- Say in the README scope that the data is synthetic
- Add the OCR text of two PPB quarterly pharmacovigilance reports
- Add the generated changelog and say how to generate it again
- Say that the changelog is part of the merge process
- Add the sources for the synthetic data research
- Log PR 1 of the synthetic data work
- Log PR 2 of the synthetic data work
- Log PR 3 of the synthetic data work
- Log PR 4 of the synthetic data work
- Log PR 5 of the synthetic data work
- Log PR 6a of the synthetic data work
- Add the results of the models on the synthetic data
- Log PR 6b of the synthetic data work
- **client:** Describe the new data and its limits on the About page and the Prediction tab
- **ml:** Describe the data, the feature sets, the experiment and the results
- Log PR 7 of the synthetic data work


### Features
- **client:** Add better auth server and client config
- **server:** Verify better auth jwts and api keys
- **client:** Add api keys page
- **client:** Use better auth for login, signup and api calls
- **client:** Add script to migrate legacy users to better auth
- **server:** Store app data in turso when configured
- **client:** Navigate with a collapsible sidebar
- **server:** Record changes in a generic audit log
- **server:** Record the signed-in user as the audit actor
- **server:** Keep history when an adr is edited, deleted or restored
- **server:** Add adr history, activity and restore endpoints
- **server:** Filter and search the adr list in the database
- **client:** Add tested helpers for the adr table
- **client:** Add restore and list filters to the adr api
- **client:** Search, filter and act on adrs from the table
- **client:** Add a tested conversion between adr records and the form
- **client:** Add putAdr to the adr api
- **client:** Load and save an adr in the edit form
- **client:** Add an edit button to the adr page
- **server:** Summarise audit entries and list deleted adrs
- **client:** Describe audit entries as readable history items
- **client:** Add the audit api calls
- **client:** Show an adr's history on a tab
- **client:** List and restore recently deleted adrs
- **client:** Add tested draft storage, change detection and required fields
- **client:** Start Add blank, offer drafts back and guard unsaved changes
- **client:** Add tested section status and progress rules for the adr form
- **client:** Show form progress and problems in a section list
- **server:** Search institutions by mfl and dhis code
- **client:** Add tested rules for institutions and the picker
- **client:** Pick an institution by searching, and add a missing one in place
- **client:** Add tested wording for the saved-report banner
- **client:** Show the result and next steps after saving an adr
- **client:** Show a progress bar while a page loads
- **client:** Explain causality levels in tooltips
- **client:** Add tested review rules and the review api calls
- **client:** Rebuild the review form so it saves
- **client:** Add tested rules for the adr details view
- **client:** Rebuild the adr details tab to be readable
- **server:** Filter the adr list by several values and sort it
- **client:** Multiselect filters and sortable columns on the adr list
- **client:** Show the dashboard charts in titled cards with all states
- **client:** Turn the home page into a start page with counts
- **client:** Tell the story of a case on the about page
- **client:** Keep the adr tab in the address and show options as badges
- **client:** Show the prediction explanation as bars and plain facts
- **server:** Tell each list row whether the signed-in user reviewed it
- **client:** Show who needs to review on the adr list, and link to each tab
- **ml:** Add a store for versions of the model
- **ml:** Add a script that exports the model from Databricks
- **server:** Load the model from the model store instead of MLflow
- **server:** Add the first model version, trained with the repository code
- **ml:** Add pure functions that measure a model for an experiment run
- **ml:** Track training experiments with MLflow in a local folder
- **server:** Replace the model version with one trained under tracking
- **ml:** Add functions that make the MLflow runs folder portable
- **ml:** Keep the runs folder portable when training ends
- **ml:** Make the data generation notebook reproducible
- **ml:** Add the shared pipeline builder
- **ml:** Add the estimator candidates
- **ml:** Add the selection file that links the experiment to the training
- **ml:** Add the experiment that selects the production model (#146)
- **ml:** Train the production model from selection.json (#148)
- **client:** Make the About page public and send signed-out visitors from Home to About
- **client:** Show the About page without the sidebar to a visitor who is not signed in
- **client:** Link the logo on the login and signup pages to the About page
- **ml:** Add the WHO-UMC rules as one pure function
- **ml:** Map the yellow form fields to the WHO-UMC facts
- **ml:** Add the PPB report totals as a checked data module
- **ml:** Sample a synthetic case in causal order
- **ml:** Generate the dataset from the sampler and validate it
- **ml:** Add the first WHO-UMC dataset of 30,000 rows and its report
- **ml:** Load the training frame for one feature set and refuse diagnostic columns
- **ml:** Add the features of the new report fields
- **ml:** Run the experiment and the training on a feature set and report recall of certain
- **ml:** Add the report of the model results
- **ml:** Select the models on the WHO-UMC data
- **ml:** Train the production model on the WHO-UMC data


### Performance
- **server:** Look up audit versions in one query per flush


### Refactoring
- **server:** Remove custom jwt auth endpoints and password hashing
- **client:** Split auth code into testable modules
- **server:** Use only the newest causality assessment per adr
- **client:** One adrs link, and remove the reviews and assessment pages
- **client:** Show only the picker for the institution in the adr form
- **client:** Share one table between the communication pages
- **server:** Move the medilinda_ml package into the server source
- **server:** Build the model input frame in one function
- **ml:** Save the trained model to the model store, and switch MLflow logging off
- **ml:** Move the golden file code into its own module
- **ml:** Move the root medilinda_ml folder into the package
- **ml:** Train with the shared pipeline and candidates


### Tests
- **client:** Cover the better auth flow
- **server:** Cover jwt and api key edge cases
- **server:** Run the audit lifecycle through the libsql driver
- **client:** Fail when a page uses a component that does not exist
- **server:** Fix the module paths that a saved model stores

## [0.1.0-alpha] - 2025-10-06

### Bug fixes
- Cleaned up server folder
- **env:** Added example env file
- **dosc:** Updated server readme
- **api:** Added dependencies
- **api:** Removed redundant '/api/v1' from endpoints
- Added config and lifespan files deleted by mistake
- **api:** Updated order of apis to prevent errors
- **basemodels:** Removed unnecessary user basemodels
- **models:** Added disabled attribute to uaser
- Removing notebooks from language stats


