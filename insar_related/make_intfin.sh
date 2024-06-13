#this scripts is used to make file intf.in based on pairs inside intf
cd intf
for i in `ls -d *`;do
    cat ../logs_intf/$i.in >> intf.in
done
mv intf.in ../
