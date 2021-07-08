# USTC_Daily_Report
A script for sending daily report automatically.



### Usage

- Fork this repository to your account and clone your own repository.

  ```bash
  git clone <your GitHub username>/USTC_Daily_Report
  ```

- Modify the values in `config.json` according your own situation.

- Modify line 7 in `.github/workflows/daily_report.yaml` to set the UTC time that you want to send your daily report. **Note:** The sending of the report may be delayed for several minutes due to the high load of Github Actions. Please refer to https://docs.github.com/en/actions/reference/events-that-trigger-workflows#scheduled-events for the detail of POSIX cron syntax.

- Push these modified files to your own repository and you can go to the Actions tab to check out whether the report has been sent successfully.

  ```bash
  git push origin main
  ```

