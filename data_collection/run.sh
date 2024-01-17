echo "run.sh <dataset_name> <open_world:cw/ow>"

$workdir='/workspaces'
# Parameter
num_batch='10'
outputdir=$workdir'/wfpdata/dataset_'$1'_'$2/
urls_file=$PWD'/input/closeworld.csv'
tbbpath=$workdir'/tor-browser'
torrc_dir_path=$workdir'/torrcs/'

echo "result_path: "$result_path
echo "torrc_dir_path: " $torrc_dir_path
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
python3 data_collector.py --scenario $2 --urls_file ${urls_file} --batch ${num_batch} --urls_openworld ${urls_openworld} --outputdir ${outputdir} --tbbpath ${tbbpath} --torrc_dir_path ${torrc_dir_path} ${ewfd}
