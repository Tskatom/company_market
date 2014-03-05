warn=$1
surr=$2
python /home/vic/work/scratch/prototype/s3_put.py -p incoming/predictions/civilunrest/icews files $1
python /home/vic/work/scratch/prototype/s3_put.py -p surrogates/civilunrest/icews files $2
