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
-- Table structure for table `tablon_investigacion_congo`
--

DROP TABLE IF EXISTS `tablon_investigacion_congo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tablon_investigacion_congo` (
  `code_module` text,
  `code_presentation` text,
  `id_student` text,
  `gender` text,
  `region` text,
  `highest_education` text,
  `imd_band` text,
  `age_band` text,
  `num_of_prev_attempts` double DEFAULT NULL,
  `studied_credits` double DEFAULT NULL,
  `disability` text,
  `final_result` text,
  `education_ordinal` bigint DEFAULT NULL,
  `age_band_ordinal` bigint DEFAULT NULL,
  `imd_band_ordinal` bigint DEFAULT NULL,
  `final_result_ordinal` bigint DEFAULT NULL,
  `gender_encoded` bigint DEFAULT NULL,
  `disability_encoded` bigint DEFAULT NULL,
  `nota_promedio` double DEFAULT NULL,
  `nota_maxima` double DEFAULT NULL,
  `nota_minima` double DEFAULT NULL,
  `total_evaluaciones_entregadas` double DEFAULT NULL,
  `porcentaje_entregas_a_tiempo` double DEFAULT NULL,
  `total_clicks_plataforma` double DEFAULT NULL,
  `clicks_dataplus` bigint DEFAULT NULL,
  `clicks_dualpane` bigint DEFAULT NULL,
  `clicks_externalquiz` bigint DEFAULT NULL,
  `clicks_folder` bigint DEFAULT NULL,
  `clicks_forumng` double DEFAULT NULL,
  `clicks_glossary` bigint DEFAULT NULL,
  `clicks_homepage` bigint DEFAULT NULL,
  `clicks_htmlactivity` bigint DEFAULT NULL,
  `clicks_oucollaborate` bigint DEFAULT NULL,
  `clicks_oucontent` double DEFAULT NULL,
  `clicks_ouelluminate` bigint DEFAULT NULL,
  `clicks_ouwiki` bigint DEFAULT NULL,
  `clicks_page` double DEFAULT NULL,
  `clicks_questionnaire` bigint DEFAULT NULL,
  `clicks_quiz` bigint DEFAULT NULL,
  `clicks_repeatactivity` bigint DEFAULT NULL,
  `clicks_resource` double DEFAULT NULL,
  `clicks_sharedsubpage` bigint DEFAULT NULL,
  `clicks_subpage` bigint DEFAULT NULL,
  `clicks_url` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-07-12 23:39:27
