-- Script per aggiornare la struttura della tabella player
-- Aggiunge le colonne per quotazioni iniziali/attuali e FVM

-- Rimuovi le vecchie colonne
ALTER TABLE player DROP COLUMN IF EXISTS quotazione_classico;
ALTER TABLE player DROP COLUMN IF EXISTS quotazione_mantra;

-- Aggiungi le nuove colonne
ALTER TABLE player ADD COLUMN IF NOT EXISTS quotazione_iniziale_classico INTEGER;
ALTER TABLE player ADD COLUMN IF NOT EXISTS quotazione_attuale_classico INTEGER;
ALTER TABLE player ADD COLUMN IF NOT EXISTS quotazione_iniziale_mantra INTEGER;
ALTER TABLE player ADD COLUMN IF NOT EXISTS quotazione_attuale_mantra INTEGER;
ALTER TABLE player ADD COLUMN IF NOT EXISTS fvm_classico INTEGER;
ALTER TABLE player ADD COLUMN IF NOT EXISTS fvm_mantra INTEGER;

-- Verifica la struttura aggiornata
\d player
