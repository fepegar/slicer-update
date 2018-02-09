conda create -n py2 python=2 -y
source activate py2
conda install -c asmeurer beautiful-soup -y 
conda install -c anaconda lxml -y
cd
mkdir -p git
cd git
git clone https://github.com/fepegar/slicer-update.git
# Supposing ~/bin is in PATH
ln -s $pwd/slicer-update/update_slicer.sh ~/bin/update_slicer
