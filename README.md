# Campus facility reporting: report form (v1)

## 1. Run locally (no Azure needed)
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```
Submit a few reports. Each one appears in `./local_data/` as a JSON file.

## 2. Create the Azure storage (one account holds both table and photos)
```bash
az login
az group create --name rg-campus-reports --location eastus
az storage account create --name <uniquename> --resource-group rg-campus-reports \
  --location eastus --sku Standard_LRS --allow-blob-public-access false
az storage account show-connection-string --name <uniquename> \
  --resource-group rg-campus-reports --query connectionString -o tsv
```
`<uniquename>`: 3-24 characters, lowercase letters and numbers only.

Copy `.env.example` to `.env` and paste the connection string. Run the app again:
reports now go to Table Storage (`reports`) and photos to Blob Storage
(`report-photos`). Check them in the Azure portal under the storage account
(Storage browser).

## 3. Deploy to Azure App Service
```bash
az webapp up --name <app-name> --resource-group rg-campus-reports \
  --runtime "PYTHON:3.11" --sku B1
az webapp config set --name <app-name> --resource-group rg-campus-reports \
  --web-sockets-enabled true \
  --startup-file "python -m streamlit run app.py --server.port 8000 --server.address 0.0.0.0"
az webapp config appsettings set --name <app-name> --resource-group rg-campus-reports \
  --settings AZURE_STORAGE_CONNECTION_STRING="<your connection string>"
```
Your live link is `https://<app-name>.azurewebsites.net`.

## Notes
- Photos are stored in a private container. The staff dashboard (next milestone)
  will need short-lived SAS links to display them.
- Set a budget alert in Azure Cost Management so you never get surprised.
- Delete everything when done: `az group delete --name rg-campus-reports`
- Before sharing publicly, remove `st.exception(e)` in `app.py`.
