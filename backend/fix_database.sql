-- Script SQL pour corriger la taille du champ image_gif
-- À exécuter directement sur la base de données PostgreSQL

-- Vérifier la structure actuelle
SELECT column_name, data_type, character_maximum_length
FROM information_schema.columns
WHERE table_name = 'machines_machine' AND column_name = 'image_gif';

-- Modifier la taille du champ
ALTER TABLE machines_machine ALTER COLUMN image_gif TYPE VARCHAR(500);

-- Vérifier la modification
SELECT column_name, data_type, character_maximum_length
FROM information_schema.columns
WHERE table_name = 'machines_machine' AND column_name = 'image_gif';