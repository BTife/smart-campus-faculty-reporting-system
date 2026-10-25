# Smart Campus Faculty Reporting System

An AI-assisted tool for reporting and triaging campus maintenance issues. Students describe a problem in plain language (with an optional photo), and the system turns it into a structured, prioritized ticket for the people who fix it.

**Live demo:** https://scfrsapp.azurewebsites.net
*(Hosted on a free tier, so the first load after a quiet period can take a minute.)*

![Report form](docs/form-screenshot.png)

## The problem

Campus issues like leaking taps, broken lights and dead projectors often go unreported because reporting is slow and form-heavy. When reports do arrive, they are vague and inconsistent, and staff spend time sorting them by hand.

This project makes reporting a 30-second task for students and gives staff reports that are already categorized and ranked by urgency.

## How it works

```
Student -> Streamlit form -> Validation -> Azure Table Storage (report text, status)
                                       \-> Azure Blob Storage (photo)
                            (next)     -> LLM extraction -> category, urgency, summary
```

1. A student describes the issue, optionally picks a building, and attaches a photo.
2. The app validates the input: text length, photo size, and a check that the upload is a real image.
3. The report is saved to Azure Table Storage, and the photo to a private Blob container.
4. *(Next)* A language model reads the text and returns structured fields (location, category, urgency, one-line summary) that staff can sort and filter by.

Because a missed safety hazard is worse than an over-flagged minor issue, the evaluation will put extra weight on catching critical reports. AI output will always appear next to the original text and photo, so staff can overrule it.

## Tech stack

- **App:** Python, Streamlit
- **Storage:** Azure Table Storage, Azure Blob Storage
- **Hosting:** Azure App Service
- **AI (in progress):** LLM API with structured JSON output

## Run it locally

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

With no Azure settings, the app runs in local mode and saves reports to a `local_data` folder. To use Azure, copy `env.example` to `.env` and add your storage account connection string.

## Roadmap

- [x] Report form with validation
- [x] Azure storage and live deployment
- [ ] Labeled test set of 30 to 50 sample reports
- [ ] Extraction prompt and evaluation (accuracy, critical-report recall, latency, cost)
- [ ] Staff dashboard sorted by urgency
- [ ] User testing and write-up
- [ ] Photo understanding, duplicate detection, daily digest (stretch)
