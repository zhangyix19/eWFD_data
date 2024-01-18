if [[ $2 != "cw" ]] && [[ $2 != "ow" ]]; then
    echo "run.sh <dataset_name> <open_world:cw/ow>"
    exit 1
fi
workdir='/work'
# Parameter
num_batch='10'
output_dir=$workdir'/wfpdata/dataset_'$1'_'$2/
urls_file=$PWD'/input/closeworld.csv'
tbbpath=$workdir'/tor-browser'
torrc_dir=$workdir'/torrcs/'

echo "workdir: "$workdir
echo "output_dir: "$output_dir
echo "torrc_dir: " $torrc_dir
echo "num_batch: " $num_batch

if [[ $1 =~ "ewfd" ]]; then
    echo "enable ewfd: True"
    ewfd="--ewfd"
else
    echo "enable ewfd: False"
    ewfd=""
fi

# kill existing tor
pkill tor

# remove data
rm -rf ${result_path}

# Data collection
python3 data_collector.py --scenario $2 --urls_file ${urls_file} --batch ${num_batch} --output_dir ${output_dir} --tbbpath ${tbbpath} --torrc_dir ${torrc_dir} ${ewfd}
