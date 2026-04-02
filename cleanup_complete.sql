-- ============================================================================
-- PostgreSQL Complete Database Cleanup Script
-- ============================================================================
-- ATTENTION: Cette script SUPPRIME COMPLÈTEMENT toutes les données
-- Ne peut PAS être annulée - assurez-vous de vouloir vraiment le faire!
-- ============================================================================

-- Supprimer toutes les données de trajectoires
DELETE FROM trajectories;
-- Supprimer toutes les données de perturbations
DELETE FROM disruptions;
-- Supprimer tous les vols
DELETE FROM flights;
-- Supprimer tous les éclairs
DELETE FROM lightning;

-- ============================================================================
-- VÉRIFICATION: Afficher le nombre d'enregistrements restants
-- ============================================================================
SELECT 'lightning' as table_name, COUNT(*) as remaining_records FROM lightning
UNION ALL
SELECT 'flights', COUNT(*) FROM flights
UNION ALL
SELECT 'disruptions', COUNT(*) FROM disruptions
UNION ALL
SELECT 'trajectories', COUNT(*) FROM trajectories;

-- ============================================================================
-- Résultat attendu: Tous les counts à 0
-- ============================================================================
-- ✅ Si tous les chiffres sont 0: Base de données nettoyée avec succès!
-- ✅ Prête pour recevoir des données pures provenant uniquement des APIs
-- ============================================================================
