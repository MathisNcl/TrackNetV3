import os
import cv2
import pandas as pd
from pathlib import Path
from  glob import glob
import random
import shutil

random.seed(42)
# Configuration
source_data = "/Users/mathisnicoli/Desktop/Projets/padel_soulaimane/Dataset"
output_folder = "raw_data"  # Format TrackNetV3

os.makedirs(output_folder, exist_ok=True)

def create_video_and_csv(game, clip, clip_path):
    # Nom de sortie
    output_name = f"{game}_{clip}"
    video_path = os.path.join(output_folder, f"{output_name}.mp4")
    csv_path = os.path.join(output_folder, f"{output_name}_ball.csv")
    
    # Lire le Label.csv
    label_csv = os.path.join(clip_path, 'Label.csv')
    if not os.path.exists(label_csv):
        print(f"Pas de Label.csv dans {clip_path}")
        return
    
    df = pd.read_csv(label_csv)
    
    # Récupérer les images et dimensions
    first_img_path = os.path.join(clip_path, df.iloc[0]['file name'])
    first_img = cv2.imread(first_img_path)
    if first_img is None:
        print(f"Impossible de lire {first_img_path}")
        return
    
    height, width = first_img.shape[:2]
    
    # Créer la vidéo
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    video = cv2.VideoWriter(video_path, fourcc, 25.0, (width, height))
    
    # Préparer le CSV
    csv_data = []
    
    for frame_idx, row in df.iterrows():
        filename = row['file name']
        visibility = row['visibility']
        x = row['x-coordinate']
        y = row['y-coordinate']
        
        # Lire et ajouter l'image à la vidéo
        img_path = os.path.join(clip_path, filename)
        img = cv2.imread(img_path)
        
        if img is not None:
            video.write(img)
            
            # Normaliser les coordonnées (0-1)
            x_norm = x / width if visibility == 1 and x >= 0 else 0
            y_norm = y / height if visibility == 1 and y >= 0 else 0
            
            csv_data.append({
                'Frame': frame_idx,
                'Ball': visibility,
                'x': round(x_norm, 3),
                'y': round(y_norm, 3)
            })
    
    video.release()
    
    # Sauvegarder le CSV
    csv_df = pd.DataFrame(csv_data)
    csv_df.to_csv(csv_path, index=False)
    
    print(f"Créé: {output_name}.mp4 et {output_name}.csv ({len(csv_data)} frames)")

# Parcourir tous les games et clips
for game in sorted(os.listdir(source_data)):
    game_path = os.path.join(source_data, game)
    if not os.path.isdir(game_path):
        continue
    
    for clip in sorted(os.listdir(game_path)):
        clip_path = os.path.join(game_path, clip)
        if not os.path.isdir(clip_path):
            continue
        
        create_video_and_csv(game, clip, clip_path)



all_games = glob("raw_data/*.mp4")
nb_games = len(all_games)
print(f"Créé {nb_games} jeux de données")
nb_games_to_select = int(nb_games * 0.1)
selected_games = random.sample(all_games, nb_games_to_select)
print("Tirage de validation: {} games".format(nb_games_to_select))

os.makedirs(output_folder.replace("raw_data", "raw_data2"), exist_ok=True)

for game in selected_games:
    shutil.move(game, output_folder.replace("raw_data", "raw_data2"))
    shutil.move(game.replace(".mp4", ".csv"), output_folder.replace("raw_data", "raw_data2"))

print(f"\nTerminé! Fichiers créés dans {output_folder}/")

os.rename()