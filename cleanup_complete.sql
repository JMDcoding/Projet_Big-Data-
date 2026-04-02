-- ============================================================================
-- PostgreSQL Complete Database Cleanup Script
-- ============================================================================
-- ATTENTION: Cette script SUPPRIME COMPLÈTEMENT toutes les données
-- Ne peut PAS être annulée - assurez-vous de vouloir vraiment le faire!
-- ============================================================================

-- Supprimer tous les éclairs
DELETE FROM lightning_strikes;
-- Supprimer toutes les perturbations de vol
DELETE FROM flight_disruptions;

-- ============================================================================
-- VÉRIFICATION: Afficher le nombre d'enregistrements restants
-- ============================================================================
SELECT 'lightning_strikes' as table_name, COUNT(*) as remaining_records FROM lightning_strikes
UNION ALL
SELECT 'flight_disruptions', COUNT(*) FROM flight_disruptions;

-- ============================================================================
-- Résultat attendu: Tous les counts à 0
-- ============================================================================
-- ✅ Si tous les chiffres sont 0: Base de données nettoyée avec succès!
-- ✅ Prête pour recevoir des données pures provenant uniquement des APIs
-- ============================================================================
