-- MySQL dump 10.13  Distrib 8.0.20, for Win64 (x86_64)
--
-- Host: 127.0.0.1    Database: oulad
-- ------------------------------------------------------
-- Server version	8.0.20

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Temporary view structure for view `v_full_domain_assess`
--

DROP TABLE IF EXISTS `v_full_domain_assess`;
/*!50001 DROP VIEW IF EXISTS `v_full_domain_assess`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_full_domain_assess` AS SELECT 
 1 AS `id_student`,
 1 AS `id_assessment`,
 1 AS `date_submitted`,
 1 AS `is_banked`,
 1 AS `score`,
 1 AS `code_module`,
 1 AS `code_presentation`,
 1 AS `assessment_type`,
 1 AS `date_planned`,
 1 AS `weight`*/;
SET character_set_client = @saved_cs_client;

--
-- Temporary view structure for view `v_full_domain_vle`
--

DROP TABLE IF EXISTS `v_full_domain_vle`;
/*!50001 DROP VIEW IF EXISTS `v_full_domain_vle`*/;
SET @saved_cs_client     = @@character_set_client;
/*!50503 SET character_set_client = utf8mb4 */;
/*!50001 CREATE VIEW `v_full_domain_vle` AS SELECT 
 1 AS `code_module`,
 1 AS `code_presentation`,
 1 AS `id_student`,
 1 AS `id_site`,
 1 AS `date`,
 1 AS `sum_click`,
 1 AS `activity_type`,
 1 AS `week_from`,
 1 AS `week_to`*/;
SET character_set_client = @saved_cs_client;

--
-- Final view structure for view `v_full_domain_assess`
--

/*!50001 DROP VIEW IF EXISTS `v_full_domain_assess`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_full_domain_assess` AS select `sa`.`id_student` AS `id_student`,`sa`.`id_assessment` AS `id_assessment`,`sa`.`date_submitted` AS `date_submitted`,`sa`.`is_banked` AS `is_banked`,`sa`.`score` AS `score`,`a`.`code_module` AS `code_module`,`a`.`code_presentation` AS `code_presentation`,`a`.`assessment_type` AS `assessment_type`,`a`.`date` AS `date_planned`,`a`.`weight` AS `weight` from (`studentassessment` `sa` join `assessments` `a` on((`sa`.`id_assessment` = `a`.`id_assessment`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;

--
-- Final view structure for view `v_full_domain_vle`
--

/*!50001 DROP VIEW IF EXISTS `v_full_domain_vle`*/;
/*!50001 SET @saved_cs_client          = @@character_set_client */;
/*!50001 SET @saved_cs_results         = @@character_set_results */;
/*!50001 SET @saved_col_connection     = @@collation_connection */;
/*!50001 SET character_set_client      = utf8mb4 */;
/*!50001 SET character_set_results     = utf8mb4 */;
/*!50001 SET collation_connection      = utf8mb4_0900_ai_ci */;
/*!50001 CREATE ALGORITHM=UNDEFINED */
/*!50013 DEFINER=`root`@`localhost` SQL SECURITY DEFINER */
/*!50001 VIEW `v_full_domain_vle` AS select `sv`.`code_module` AS `code_module`,`sv`.`code_presentation` AS `code_presentation`,`sv`.`id_student` AS `id_student`,`sv`.`id_site` AS `id_site`,`sv`.`date` AS `date`,`sv`.`sum_click` AS `sum_click`,`v`.`activity_type` AS `activity_type`,`v`.`week_from` AS `week_from`,`v`.`week_to` AS `week_to` from (`studentvle` `sv` join `vle` `v` on((`sv`.`id_site` = `v`.`id_site`))) */;
/*!50001 SET character_set_client      = @saved_cs_client */;
/*!50001 SET character_set_results     = @saved_cs_results */;
/*!50001 SET collation_connection      = @saved_col_connection */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-07-12 23:39:28
