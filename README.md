# Energy consumption

Forecast daily electricity consumption in a **Job**, and explore it in a public **Streamlit App**.

This project belongs to a Renku **hands-on workshop** at SDSC aiming to share how to create jobs and apps in Renku. Each participant submits a **Job** (non-interactive run) and publishes an **App** (public web app) from this repo.

> **Data rule:** Renku apps run only on **public** projects. 

## What's inside

| Path | Role |
| --- | --- |
| `train.py` | **Job**: holds out the last N days, fits a Ridge forecast, prints MAE, writes a CSV |
| `src/app.py` | **App**: Streamlit dashboard |
| `src/model.py` | Model shared by job and app |
| `Procfile` | One line that tells Renku how to start the app (`web:` binds `0.0.0.0` and `$RENKU_SESSION_PORT`) |

## Renku project setup

1. Fork the code repository `https://github.com/bethcg/renku-workshop-energy-forecasting`.
2. Create a new project in Renku, set it to **public**, and add:
   - **Data connector with input data**: [link to your project the already existing data connector](https://docs.renkulab.io/en/latest/docs/users/data/guides/link-data-connector-to-project/) containing the input data, `renku-team/energy-consumption-forecast/energy-consumption-input-data`.
   - **Code repository**: your fork. [Add a code repository](https://docs.renkulab.io/en/latest/docs/users/code/guides/add-code-repository-to-project/)
   - **Storage for job results (Optional)**: either option from *Where to keep job results* below.
   - **Session launcher**: *Create from code*, using the requirements defined in the code repository. [Create an environment with custom packages](https://docs.renkulab.io/en/latest/docs/users/compute/environment/guides/create-environment-with-custom-packages-installed/)
3. Start the session launcher once to check that the environment builds. The first build takes a few minutes.

### Where to keep job results

Jobs have no persistent disk of their own, so results must go to storage that is mounted into the job.

| Option | How to get it | Access | Notes |
| --- | --- | --- | --- |
| **Data connector to a PolyBox / SWITCHdrive shared folder** | [Connect a shared folder](https://docs.renkulab.io/en/latest/docs/users/data/guides/connect-data/connect-shared-switchdrive-or-polybox-folder-to-project/) with **read/write** permissions | Needs your credentials when the job starts | Results also show up in your PolyBox / SWITCHdrive |
| **Renku project storage** | Limited rollout: email [hello@renku.io](mailto:hello@renku.io) with your project name, then create it from the new tab in the data connector menu | Owners and editors read/write; viewers read-only; **anonymous users have no access, even on public projects** | Mounted in every session and job of the project; shared with project members; persists across pauses and shutdowns |

The **App can't read either option**. Apps only mount public, credential-free data connectors, and anonymous app visitors have no access to project storage.

## Set up the `rnk` CLI

The `rnk` CLI lets you start and follow jobs (and sessions) from your terminal. Install it on your laptop, not inside a session.

1. **Install**
   - macOS / Linux:
     ```bash
     curl -sfSL https://raw.githubusercontent.com/SwissDataScienceCenter/renku-cli/main/install.sh | bash
     ```
   - Windows, or as a manual alternative: download the binary from the [releases page](https://github.com/SwissDataScienceCenter/renku-cli/releases/latest) (`*-darwin` for macOS, `*-amd64` / `*-aarch64` for Linux, `*-windows` for Windows), make it executable, and put it on your `PATH`.
2. **Enable shell completions** (recommended, so you can tab-complete launcher and job IDs):
   ```bash
   echo "source <(COMPLETE=zsh rnk)" >> ~/.zshrc     # zsh (macOS default)
   echo "source <(COMPLETE=bash rnk)" >> ~/.bashrc   # bash
   ```
   Then open a new terminal.
3. **Log in** (opens an interactive login):
   ```bash
   rnk login
   ```
4. **Select your workshop project**, so you don't need to pass it to every command:
   ```bash
   rnk project list                               # find your project
   rnk project activate <namespace>/<project-slug>
   rnk project current                            # check
   ```
5. **Check that it works**:
   ```bash
   rnk version
   rnk launcher list
   ```

Full reference: [Renku CLI](https://docs.renkulab.io/en/latest/docs/users/cli/cli-reference/).

## Exercise 1: Job

### In the Renku UI

1. In your Renku project, add a launcher of type **Job**.
2. Choose **Create from code**, select the code repository `renku-workshop-energy-forecasting`, and set the command to:
   ```json
   ["python", "renku-workshop-energy-forecasting/train.py"]
   ```
   Set the job args to:
   ```json
   ["--horizon", "7"]
   ```
   Each flag and each value is its own list item. Writing `["--horizon 7"]` passes a single argument and the script fails.
3. Click **Submit**, keep the default resource class, and open the logs.
4. Submit again with different arguments and a bigger resource class:
   ```json
   ["--horizon", "28", "--alpha", "10"]
   ```
5. Jobs don't keep files. Logs disappear when a job is dismissed, and finished jobs are removed after ~24 h. To keep results, write them to the storage you set up in *Preparation*, using either of these:
   - the argument `--out <mount path>`, e.g. `["--horizon", "7", "--out", "/home/renku/work/<connector-target-path>"]`
   - an [environment variable](https://docs.renkulab.io/en/latest/docs/users/compute/session/guides/share-session-launch-link/#make-launch-links-even-smarter-with-environment-variables) on the job launcher: `OUTPUT_DIR` = your mount path. `--out` overrides it if both are set.

### The same job from the CLI

```bash
rnk launcher list --mode non-interactive          # copy the ID of your job launcher
rnk job start --launcher <launcher-id> --wait -- --horizon 14
rnk job list                                      # all your jobs and their IDs
rnk job logs <job-id>                             # logs of a finished job
```

- `--wait` streams the logs until the job ends (Ctrl-C stops following; the job keeps running).
- Everything after `--` replaces the launcher's job args for this run only.
- `--command` overrides the launcher's command, and `--submission-id <name>` gives the run a readable name.

## Exercise 2: App

The app is a Streamlit dashboard with a period filter, KPIs, the daily series with a 7-day average, and a forecast check.

1. Make sure the Renku project is **public**.
2. Add a launcher of type **App** → **Create from code** → this repository. Renku builds with buildpacks and starts the app with the `Procfile`; no command is needed.
3. Click **Start** and wait until the status is *Live*, then click **Copy app URL** and share it. Share the Renku URL, not the address your browser lands on after the app opens.

## Run locally

```bash
pip install -r requirements.txt
python train.py --horizon 7
streamlit run src/app.py --server.port 8000
```

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| App stuck in Starting → Failed | Server must listen on `0.0.0.0` and `$RENKU_SESSION_PORT` |
| Start button greyed out | Project not public, build unfinished, no write access, or another app is already running in the project |
| Changes not visible | Stop and Start the app again after editing the launcher |
| Job results gone | Write to a data connector with `--out` |

## Data

`consumption.csv` is **synthetic**, generated with realistic seasonality (winter peak, weekends lower, temperature-driven heating). It is not real Swiss grid data. To use real data, write a CSV with the columns `date, consumption_gwh, temperature_c` (e.g. from [opendata.swiss](https://opendata.swiss)).

## Docs

- [Renku Jobs](https://docs.renkulab.io/en/latest/docs/users/compute/job/)
- [Renku Apps](https://docs.renkulab.io/en/latest/docs/users/compute/app/) · [Publish an app](https://docs.renkulab.io/en/latest/docs/users/compute/app/guides/host-app)
- [Renku CLI](https://docs.renkulab.io/en/latest/docs/users/cli/cli-reference/) · [renku-cli on GitHub](https://github.com/SwissDataScienceCenter/renku-cli)
