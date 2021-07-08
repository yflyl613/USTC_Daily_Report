# USTC_Daily_Report
A script for sending daily report automatically.



### Usage

- Fork this repository to your account and clone your own repository.

- Modify the values in `config.json` according your own situation.

- Modify line 7 in `.github/workflows/daily_report.yaml` to set the UTC time that you want to send your daily report. Please refer to https://docs.github.com/en/actions/reference/events-that-trigger-workflows#scheduled-events for the detail of POSIX cron syntax. 

  **Note:** The sending of the report may be delayed for several minutes due to the high load of Github Actions. 

- Push these modified files to your own repository and you can go to the Actions tab to check out whether the report has been sent successfully.

  **Note:** At least one file has to be modified before pushing to your repository. You can simply insert a space at the end of `README.md` if no other files need to be modified.

