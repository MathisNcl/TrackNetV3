#!/bin/bash
set -e

# Logs
# exec > >(tee /var/log/user-data.log)
# exec 2>&1

# Mise à jour système
curl -LsSf https://astral.sh/uv/install.sh | sh
export PATH="/root/.cargo/bin:$PATH"

# Clone du repository
# git clone ${var.git_repo_url} tracknetv3
cd tracknetv3

# Création venv avec uv
/root/.cargo/bin/uv venv .venv
source .venv/bin/activate

# Installation des dépendances
/root/.cargo/bin/uv sync

# Création du dataset
mkdir TrackNetV2_Dataset
mkdir TrackNetV2_Dataset/train
mkdir TrackNetV2_Dataset/test
python zz_Tracknet_badminton_DataConvert.py --original_raw_data --target_folder "TrackNetV2_Dataset/train"
python zz_Tracknet_badminton_DataConvert.py --original_raw_data2 --target_folder "TrackNetV2_Dataset/test"

# Lancement de l'entraînement (ajustez le script selon votre besoin)
python train.py --num_frame 3 --epochs 1 --batch_size 8 --learning_rate 0.001 --save_dir exp

# Upload vers S3
aws s3 sync ./exp s3://${aws_s3_bucket.ml_results.id}/training_results/ --region ${aws_s3_bucket.ml_results.region}

# Arrêt de l'instance après upload
# shutdown -h now