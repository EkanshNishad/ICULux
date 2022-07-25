-- phpMyAdmin SQL Dump
-- version 5.1.0
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: May 21, 2021 at 03:33 PM
-- Server version: 10.4.18-MariaDB
-- PHP Version: 8.0.3

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `icu`
--

-- --------------------------------------------------------

--
-- Table structure for table `doctor`
--

CREATE TABLE `doctor` (
  `Name` varchar(255) DEFAULT NULL,
  `Age` int(11) DEFAULT NULL,
  `Doctor_id` int(11) DEFAULT NULL,
  `Email_id` varchar(255) DEFAULT NULL,
  `Password` varchar(255) DEFAULT NULL,
  `Specialization` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `doctor`
--

INSERT INTO `doctor` (`Name`, `Age`, `Doctor_id`, `Email_id`, `Password`, `Specialization`) VALUES
('Arun Kumar', 39, 12166, 'iit2019166@iiita.ac.in', 'delhisehai', 'Thoracic Surgeon'),
('Ansh Verma', 35, 12167, 'iit2019167@iiita.ac.in', 'cybergeek', 'Neurologist'),
('Prathamesh Gandhwale', 25, 12181, 'iit2019181@iiita.ac.in', 'gutendevil', 'Internists'),
('Ekansh Nishad', 32, 12182, 'iit2019182@iiita.ac.in', 'class_bunker', 'Hematologist'),
('Rajveer', 20, 12422, 'IIT2019180@iiita.ac.in', 'helloraaja', 'Surgeon');

-- --------------------------------------------------------

--
-- Table structure for table `patient_information`
--

CREATE TABLE `patient_information` (
  `pid` char(3) DEFAULT NULL,
  `Name` varchar(60) DEFAULT NULL,
  `Age` int(2) DEFAULT NULL,
  `Gender` char(19) DEFAULT NULL,
  `DOI` date DEFAULT NULL,
  `Disease` varchar(60) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `patient_information`
--

INSERT INTO `patient_information` (`pid`, `Name`, `Age`, `Gender`, `DOI`, `Disease`) VALUES
('037', 'Mithali Raj', 38, 'Female', '2021-02-01', 'Unspecified'),
('039', 'Sachin Tendulkar', 70, 'Male', '2021-02-01', 'Bleed'),
('041', 'Sachin Tendulkar', 70, 'Male', '2021-02-01', 'Bleed'),
('055', 'Virat Kohli', 38, 'Male', '2021-02-11', 'Respiratory failure'),
('208', 'Aftab Kasim', 80, 'Male', '2021-02-11', 'Bleed'),
('209', 'Aftab Kasim', 80, 'Male', '2021-02-11', 'Bleed'),
('210', 'Aftab Kasim', 80, 'Male', '2021-02-11', 'Bleed'),
('211', 'Saina Nehwal', 67, 'Female', '2021-02-12', 'Respiratory failure'),
('212', 'Johnny Lever', 84, 'Male', '2021-02-12', 'CHF/pulmonary edema'),
('213', 'Sania Mirza', 82, 'Female', '2021-02-13', 'CHF/pulmonary edema'),
('216', 'Amit Shah', 67, 'Male', '2021-02-13', 'Respiratory failure'),
('218', 'Amit Shah', 67, 'Male', '2021-02-13', 'Respiratory failure'),
('219', 'Amit Shah', 67, 'Male', '2021-02-13', 'Respiratory failure'),
('220', 'PV Sindhu', 68, 'Female', '2021-02-13', 'Brain injury'),
('221', 'PV Sindhu', 68, 'Female', '2021-02-13', 'Brain injury'),
('222', 'Sunil Chhetri', 88, 'Male', '2021-02-13', 'Sepsis'),
('224', 'Ansh Verma', 21, 'Male', '2021-02-13', 'Sepsis'),
('226', 'Kuldeep Yadav', 68, 'Male', '2021-02-14', 'CHF/pulmonary edema'),
('230', 'Harmanpreet Kaur', 75, 'Female', '2021-02-14', 'CHF/pulmonary edema'),
('231', 'Harmanpreet Kaur', 75, 'Female', '2021-02-14', 'CHF/pulmonary edema'),
('237', 'Mamta Banerjee', 63, 'Female', '2021-02-14', 'MI/cardiogenic shock'),
('240', 'Kailash Kher', 68, 'Male', '2021-02-15', 'Angina'),
('248', 'Madhuri Dixit', 80, 'Female', '2021-02-15', 'MI/cardiogenic shock'),
('252', 'Rajpal Yadav', 52, 'Male', '2021-02-15', 'Respiratory Failure'),
('253', 'Rajpal Yadav', 52, 'Male', '2021-02-15', 'Respiratory Failure'),
('254', 'Rajpal Yadav', 52, 'Male', '2021-02-15', 'Respiratory Failure'),
('260', 'Gunjan Mahato', 76, 'Female', '2021-02-16', 'CHF/pulmonary edema'),
('262', 'Kalpana Chawla', 65, 'Female', '2021-02-16', 'Post-op valve'),
('276', 'Mikasa Ackerman', 66, 'Female', '2021-02-16', 'Unspecified'),
('281', 'Uzamaki Nauto', 61, 'Male', '2021-02-17', 'Unspecified'),
('284', 'Mayawati', 59, 'Female', '2021-02-17', 'Angina'),
('291', 'Arun Kumar', 27, 'Male', '2021-02-17', 'Sepsis'),
('401', 'Anjana Om Kashyp', 64, 'Female', '2021-02-18', 'Respiratory failure'),
('403', 'Anjana Om Kashyp', 64, 'Female', '2021-02-18', 'Respiratory failure'),
('404', 'Bharti Singh', 87, 'Female', '2021-02-18', 'Respiratory failure'),
('405', 'Sunidhi Chauhan', 63, 'Female', '2021-02-19', 'MI/cardiogenic shock'),
('408', 'Ravish Kumar', 45, 'Male', '2021-02-19', 'Bleed'),
('409', 'Ravish Kumar', 45, 'Male', '2021-02-19', 'Bleed'),
('410', 'Bhuvan Bam', 57, 'Male', '2021-02-20', 'Sepsis'),
('411', 'Pronomita Chakraborty', 82, 'Female', '2021-02-20', 'Respiratory failure'),
('413', 'Aanchal Singh', 92, 'Female', '2021-02-20', 'CHF/pulmonary edema'),
('414', 'Aanchal Singh', 92, 'Female', '2021-02-20', 'CHF/pulmonary edema'),
('415', 'Shrejal Sharma', 54, 'Female', '2021-02-21', 'CHF/pulmonary edema'),
('417', 'Kapil Dev', 86, 'Male', '2021-02-21', 'CHF/pulmonary edema'),
('418', 'Rafael Nadal', 52, 'Male', '2021-02-21', 'CHF/pulmonary edema'),
('427', 'Rahul Gandhi', 48, 'Male', '2021-02-22', 'MI/arrest'),
('430', 'Harsh Garhwal', 91, 'Male', '2021-02-22', 'Unspecified'),
('437', 'Arvind Kejriwal', 75, 'Male', '2021-02-22', 'Respiratory failure'),
('438', 'Pranjal Verma', 78, 'Male', '2021-02-23', 'Sepsis'),
('439', 'Harshita Kashyp', 75, 'Female', '2021-02-23', 'Sepsis'),
('442', 'Rimjhim Pandey', 67, 'Female', '2021-02-24', 'Post-op valve'),
('443', 'Priyank Kumar', 75, 'Male', '2021-02-24', 'Respiratory failure'),
('444', 'Priyank Kumar', 75, 'Male', '2021-02-24', 'Respiratory failure'),
('446', 'Chirag Gajbhiye', 73, 'Male', '2021-02-24', 'Sepsis'),
('449', 'Ekansh Nishad', 75, 'Male', '2021-02-25', 'Brain injury'),
('450', 'Anshumaan Prasad', 76, 'Male', '2021-02-26', 'CHF/pulmonary edema'),
('451', 'Anshumaan Prasad', 76, 'Male', '2021-02-26', 'CHF/pulmonary edema'),
('452', 'Nishant Gupta', 73, 'Male', '2021-02-27', 'Cord compression'),
('453', 'Jagpreet Singh', 95, 'Male', '2021-02-27', 'Cord compression'),
('454', 'Eren Yeagar', 20, 'Male', '2021-02-27', 'Brain Injury'),
('456', 'Kumar Vyom', 49, 'Male', '2021-02-28', 'Post-op CABG'),
('466', 'Lelouch Vi Britannia', 84, 'Male', '2021-03-01', 'CHF/pulmonary edema'),
('471', 'Prableen Kaur', 78, 'Female', '2021-03-01', 'Renal failure'),
('472', 'Ayush Dewangan', 79, 'Male', '2021-03-02', 'Bleed'),
('474', 'Pranjal Pandey', 75, 'Male', '2021-03-02', 'Unspecified'),
('476', 'Harsha Hirwani', 72, 'Female', '2021-03-03', 'Post-op CABG'),
('477', 'Hemant Kumar', 67, 'Male', '2021-03-03', 'Post-op CABG'),
('480', 'Vigyaan Kumar', 52, 'Male', '2021-03-04', 'Post-op CABG'),
('481', 'Stuti Mishra', 73, 'Female', '2021-03-04', 'Post-op valve'),
('482', 'Divya Nair', 92, 'Female', '2021-03-05', 'Post-op valve'),
('484', 'Priyanshu Sarate', 60, 'Male', '2021-03-05', 'Unspecified'),
('485', 'Rohit Rai', 69, 'Male', '2021-03-06', 'Unspecified');
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
