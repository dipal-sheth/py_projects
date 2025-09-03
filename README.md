To install dependencies

```
source venv/bin/activate
pip install -r requirements.txt
```
## run webscrapping 
```

python src\rearc\bls_local_sync_v3.py --base-url http://download.bls.gov/pub/time.series/pr/ --dest-dir src\rearc\data\bls_data --concurrency 6  --delete
```

## run terraform
```
cd src/rearc/terraform 
terraform init
terraform validate
terraform plan -out=tfplan
terraform apply --auto-approve
```