#!/bin/bash

oak_dir="/oak/stanford/groups/russpold/data/network_test/"
local_dir="./data/test_symlink"

echo "Creating symbolic link from $oak_dir to $local_dir"

mkdir -p "$(dirname "$local_dir")"
ln -sf "$oak_dir" "$local_dir"

echo "Symbolic linking complete!"
echo "To unlink run rm $local_dir"