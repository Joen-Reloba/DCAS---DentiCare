-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Dec 18, 2025 at 11:54 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `dentalclinic`
--

-- --------------------------------------------------------

--
-- Table structure for table `dentist`
--

CREATE TABLE `dentist` (
  `StaffID` int(11) NOT NULL,
  `LicenseNum` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `dentist`
--

INSERT INTO `dentist` (`StaffID`, `LicenseNum`) VALUES
(8, '11112314'),
(27, '12312312'),
(15, '39287361'),
(14, '637183761'),
(17, '918371391'),
(6, '99999997');

-- --------------------------------------------------------

--
-- Table structure for table `patient`
--

CREATE TABLE `patient` (
  `PatientID` int(11) NOT NULL,
  `PatientFname` varchar(20) NOT NULL,
  `PatientMname` varchar(20) DEFAULT NULL,
  `PatientLname` varchar(20) NOT NULL,
  `Sex` varchar(20) NOT NULL,
  `Birthday` date DEFAULT NULL,
  `ContactNumber` varchar(20) NOT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `patient`
--

INSERT INTO `patient` (`PatientID`, `PatientFname`, `PatientMname`, `PatientLname`, `Sex`, `Birthday`, `ContactNumber`, `created_at`, `updated_at`) VALUES
(7, 'Mike', '', 'Wilde', 'male', '2000-01-01', '09293334444', '2025-12-16 20:32:42', '2025-12-16 20:32:42'),
(8, 'Nick', '', 'Wilde', 'male', '2000-01-01', '09182745261', '2025-12-16 20:32:42', '2025-12-16 20:32:42'),
(9, 'Mike', '', 'Wheeler', 'male', '2000-01-01', '09193334444', '2025-12-16 20:32:42', '2025-12-16 20:32:42'),
(11, 'Jade', '', 'Lemac', 'male', '2000-01-01', '09215556666', '2025-12-16 20:32:42', '2025-12-16 20:32:42'),
(12, 'Keshi', '', 'Keenan', 'male', '2000-01-01', '09282223333', '2025-12-16 20:32:42', '2025-12-16 20:32:42'),
(13, 'John Paul', '', 'Martinez', 'male', '1990-05-15', '09171112222', '2025-12-16 20:32:42', '2025-12-16 20:32:42'),
(14, 'Sarah', '', 'Lopez', 'female', '1985-08-20', '09182223333', '2025-12-16 20:32:42', '2025-12-16 20:32:42'),
(15, 'Lisa', 'Ann', 'Fernandez', 'female', '1995-11-25', '09204445555', '2025-12-16 20:32:42', '2025-12-16 20:32:42'),
(16, 'Daniel', '', 'Ramos', 'male', '1987-01-22', '09259990000', '2025-12-16 20:32:42', '2025-12-16 20:32:42'),
(17, 'Alexander Paul', '', 'Castro', 'male', '2000-01-01', '09315556666', '2025-12-16 20:32:42', '2025-12-16 20:32:42'),
(18, 'Nicole', '', 'Villanueva', 'female', '1994-05-09', '09304445555', '2025-12-16 20:32:42', '2025-12-16 20:32:42'),
(19, 'James', '', 'Garcia', 'female', '1991-10-03', '09271112222', '2025-12-16 20:32:42', '2025-12-16 20:32:42'),
(20, 'Leo', '', 'King', 'male', '2000-06-08', '09100000010', '2025-12-16 20:32:42', '2025-12-16 20:32:42'),
(21, 'Noah', '', 'Scott', 'male', '1999-09-09', '09100000012', '2025-12-16 20:32:42', '2025-12-16 20:32:42'),
(22, 'Ben', '', 'Ten', 'male', '1889-12-10', '09100000020', '2025-12-16 20:32:42', '2025-12-16 20:32:42'),
(23, 'Ella', '', 'Green', 'female', '2016-10-11', '09100000013', '2025-12-16 20:32:42', '2025-12-16 20:32:42'),
(24, 'Hopper', '', 'Haringthon', 'male', '1998-06-10', '09182748190', '2025-12-16 20:32:42', '2025-12-16 22:31:47'),
(25, 'Hopperr', '', 'Hops', 'female', '1999-12-26', '09176767181', '2025-12-16 20:32:42', '2025-12-17 07:47:50'),
(26, 'Andie', '', 'Mina', 'male', '2000-01-01', '09182364711', '2025-12-16 20:32:42', '2025-12-16 21:04:24');

-- --------------------------------------------------------

--
-- Table structure for table `services`
--

CREATE TABLE `services` (
  `ServiceID` int(11) NOT NULL,
  `ServiceName` varchar(20) NOT NULL,
  `BasePrice` decimal(10,2) NOT NULL,
  `IsVATApplicable` tinyint(1) DEFAULT 1,
  `VATRate` decimal(5,2) DEFAULT 12.00,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `services`
--

INSERT INTO `services` (`ServiceID`, `ServiceName`, `BasePrice`, `IsVATApplicable`, `VATRate`, `created_at`, `updated_at`) VALUES
(1, 'Teeth Cleaning', 800.00, 1, 12.00, '2025-12-16 20:33:51', '2025-12-17 05:59:35'),
(2, 'Braces', 10000.00, 1, 12.00, '2025-12-16 20:33:51', '2025-12-17 05:59:35'),
(4, 'Tooth Extraction', 1500.00, 1, 12.00, '2025-12-16 20:33:51', '2025-12-17 05:59:35'),
(5, 'Wisdom tooth removal', 800.00, 1, 12.00, '2025-12-16 20:33:51', '2025-12-17 05:59:35'),
(6, 'Whitening Teeth', 1500.00, 1, 12.00, '2025-12-16 20:33:51', '2025-12-17 05:59:35'),
(7, 'Dental Filling', 1200.00, 1, 12.00, '2025-12-16 20:33:51', '2025-12-17 05:59:35'),
(8, 'Tooth Implant', 45000.00, 1, 12.00, '2025-12-16 20:33:51', '2025-12-17 05:59:35'),
(9, 'Root Canal', 5000.00, 1, 12.00, '2025-12-16 20:33:51', '2025-12-17 05:59:35'),
(14, 'Jacketing', 8000.00, 1, 12.00, '2025-12-16 20:33:51', '2025-12-17 05:59:35'),
(16, 'Oral Examination', 800.00, 0, 12.00, '2025-12-17 07:19:45', '2025-12-17 11:41:41'),
(17, 'test04', 124.00, 1, 12.00, '2025-12-17 07:45:48', '2025-12-17 07:46:00'),
(18, 'testnovat', 100.00, 0, 12.00, '2025-12-17 07:48:34', '2025-12-17 07:48:34');

-- --------------------------------------------------------

--
-- Table structure for table `staff`
--

CREATE TABLE `staff` (
  `StaffID` int(11) NOT NULL,
  `StaffFname` varchar(20) NOT NULL,
  `StaffMname` varchar(20) DEFAULT NULL,
  `StaffLname` varchar(20) NOT NULL,
  `Sex` varchar(20) NOT NULL,
  `Birthday` date NOT NULL,
  `ContactNumber` varchar(20) NOT NULL,
  `Barangay` varchar(20) DEFAULT NULL,
  `City` varchar(20) NOT NULL,
  `Province` varchar(20) DEFAULT NULL,
  `Zipcode` int(11) DEFAULT NULL,
  `Role` varchar(20) NOT NULL,
  `DateHired` date NOT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `staff`
--

INSERT INTO `staff` (`StaffID`, `StaffFname`, `StaffMname`, `StaffLname`, `Sex`, `Birthday`, `ContactNumber`, `Barangay`, `City`, `Province`, `Zipcode`, `Role`, `DateHired`, `created_at`, `updated_at`) VALUES
(2, 'Joen Paul', 'Quijano', 'Reloba', 'male', '2000-01-01', '09497521911', 'Baliok', 'Davao', 'Davao Del Sur', 8000, 'admin', '2000-01-01', '2025-12-16 20:30:43', '2025-12-16 20:54:51'),
(3, 'Mika', '', 'Ella', 'female', '2000-01-01', '12348762811', 'Calinan', 'City', 'Del Sur', 0, 'frontdesk', '2000-01-01', '2025-12-16 20:30:43', '2025-12-16 20:55:03'),
(6, 'Cristy', '', 'Amihan', 'female', '2000-01-01', '126819271', 'Bato', 'Davao', 'Davao Del Sur', 8000, 'dentist', '2000-01-01', '2025-12-16 20:30:43', '2025-12-16 20:30:43'),
(8, 'Judy', '', 'Hopp', 'female', '1999-12-28', '12345671237', 'Crossing Bayabas', 'Davao', 'Del Sur', 800, 'dentist', '2000-01-01', '2025-12-16 20:30:43', '2025-12-16 20:30:43'),
(10, 'Mikha', 'Miks', 'Lim', 'female', '2004-05-06', '0912736171', '', 'Davao City', '', 0, 'admin', '2000-01-01', '2025-12-16 20:30:43', '2025-12-16 20:30:43'),
(11, 'Mikie', 'Nigs', 'Akwards', 'female', '1997-07-02', '1345654321', 'Toril', 'Davao City', '', 0, 'frontdesk', '2000-01-01', '2025-12-16 20:30:43', '2025-12-16 20:30:43'),
(14, 'Juan', 'Cruz', 'Dela Cruz', 'male', '1980-07-22', '09181234567', 'Matina', 'Davao City', 'Davao del Sur', 8000, 'dentist', '2020-02-15', '2025-12-16 20:30:43', '2025-12-16 20:30:43'),
(15, 'Ana', 'Marie', 'Santos', 'female', '1990-11-08', '09191234567', 'Agdao', 'Davao City', 'Davao del Sur', 8000, 'dentist', '2020-03-01', '2025-12-16 20:30:43', '2025-12-16 20:30:43'),
(16, 'Pedro', NULL, 'Garcia', 'male', '1995-05-12', '09201234567', 'Buhangin', 'Davao City', 'Davao del Sur', 8000, 'frontDesk', '2021-06-15', '2025-12-16 20:30:43', '2025-12-16 20:30:43'),
(17, 'Rosa', 'Linda', 'Torres', 'female', '1988-09-30', '09211234567', 'Toril', 'Davao City', 'Davao del Sur', 8000, 'dentist', '2021-08-20', '2025-12-16 20:30:43', '2025-12-16 20:30:43'),
(18, 'Carlos', 'Miguel', 'Ramos', 'male', '1992-01-18', '09221234567', 'Talomo', 'Davao City', 'Davao del Sur', 8000, 'frontDesk', '2022-01-10', '2025-12-16 20:30:43', '2025-12-16 20:30:43'),
(19, 'Miguel', '', 'Miguelito', 'male', '1999-12-27', '09274615281', 'Bato', 'Davao City', '', 0, 'admin', '2000-01-01', '2025-12-16 20:30:43', '2025-12-16 20:30:43'),
(22, 'Jaypee', '', 'Peejay', 'male', '2000-01-13', '09182742819', 'Bato', 'Davao Del Sur', 'Davao Del Sur', 8000, 'frontdesk', '2000-01-01', '2025-12-16 20:30:43', '2025-12-16 20:30:43'),
(23, 'Mike', '', 'Mouse', 'female', '1998-05-21', '09187676111', 'Talomo', 'Davao City', 'Davao Del Sur', 8000, 'frontdesk', '2025-12-09', '2025-12-16 20:30:43', '2025-12-17 14:01:06'),
(24, 'Joh', '', 'Damasco', 'male', '2006-05-06', '09183657182', 'Sandawa', 'Davao City', 'Davao Del Sur', 8000, 'admin', '2025-09-22', '2025-12-16 20:30:43', '2025-12-17 14:01:30'),
(25, 'Claude', '', 'Galon', 'male', '2000-01-01', '09182746511', 'Talomo', 'Davao', 'Davao del sur', 8000, 'frontdesk', '2025-12-16', '2025-12-16 20:30:43', '2025-12-16 20:30:43'),
(26, 'Nickloas', '', 'Nick', 'male', '2000-01-01', '09876152431', 'Talomo', 'Davao City', 'Davao del sur', 8000, 'frontdesk', '2025-12-16', '2025-12-16 20:30:43', '2025-12-16 20:30:43'),
(27, 'Zan', '', 'Dave', 'male', '2006-01-10', '09182745172', 'Sasa', 'Davao City', 'Davao Del Sur', 800, 'dentist', '2025-12-17', '2025-12-17 11:45:28', '2025-12-17 11:45:28');

-- --------------------------------------------------------

--
-- Table structure for table `staffcred`
--

CREATE TABLE `staffcred` (
  `StaffID` int(11) NOT NULL,
  `Username` varchar(20) NOT NULL,
  `Password` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
  `created_at` datetime DEFAULT current_timestamp(),
  `updated_at` datetime DEFAULT current_timestamp() ON UPDATE current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `staffcred`
--

INSERT INTO `staffcred` (`StaffID`, `Username`, `Password`, `created_at`, `updated_at`) VALUES
(2, 'Admin', '123', '2025-12-16 20:33:20', '2025-12-16 20:33:20'),
(3, 'frontdesk', '123', '2025-12-16 20:33:20', '2025-12-16 20:33:20'),
(10, 'Mikha', 'Miks', '2025-12-16 20:33:20', '2025-12-16 20:33:20'),
(11, 'Micki3', '1213', '2025-12-16 20:33:20', '2025-12-17 10:47:44'),
(16, 'Pedro', 'pedr1', '2025-12-16 20:33:20', '2025-12-17 04:52:45'),
(22, 'Jaypee', 'jaype3', '2025-12-16 20:33:20', '2025-12-17 04:56:34'),
(24, 'John', 'Dams', '2025-12-16 20:33:20', '2025-12-16 20:33:20'),
(25, 'Claude', 'Galon', '2025-12-16 20:33:20', '2025-12-16 20:33:20'),
(26, 'nick', 'nick9', '2025-12-16 20:33:20', '2025-12-16 20:33:20');

-- --------------------------------------------------------

--
-- Table structure for table `transactiondetails`
--

CREATE TABLE `transactiondetails` (
  `TransactionDetailsID` int(11) NOT NULL,
  `TransactionID` int(11) NOT NULL,
  `ServiceID` int(11) NOT NULL,
  `PriceAtTransaction` decimal(10,2) NOT NULL,
  `BasePrice` decimal(10,2) DEFAULT NULL,
  `VATAmount` decimal(10,2) DEFAULT 0.00,
  `VATRate` decimal(5,2) DEFAULT 12.00,
  `IsVATApplicable` tinyint(1) DEFAULT 1,
  `Quantity` int(11) DEFAULT 1
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `transactiondetails`
--

INSERT INTO `transactiondetails` (`TransactionDetailsID`, `TransactionID`, `ServiceID`, `PriceAtTransaction`, `BasePrice`, `VATAmount`, `VATRate`, `IsVATApplicable`, `Quantity`) VALUES
(6, 37, 1, 800.00, 714.29, 85.71, 12.00, 1, 1),
(7, 38, 1, 800.00, 714.29, 85.71, 12.00, 1, 1),
(8, 38, 2, 10000.00, 8928.57, 1071.43, 12.00, 1, 1),
(9, 39, 2, 10000.00, 8928.57, 1071.43, 12.00, 1, 1),
(10, 40, 1, 800.00, 714.29, 85.71, 12.00, 1, 1),
(11, 40, 2, 10000.00, 8928.57, 1071.43, 12.00, 1, 1),
(12, 41, 2, 10000.00, 8928.57, 1071.43, 12.00, 1, 2),
(13, 42, 4, 1500.00, 1339.29, 160.71, 12.00, 1, 3),
(14, 43, 4, 1500.00, 1339.29, 160.71, 12.00, 1, 2),
(15, 43, 1, 800.00, 714.29, 85.71, 12.00, 1, 1),
(16, 44, 4, 1500.00, 1339.29, 160.71, 12.00, 1, 1),
(17, 45, 4, 1500.00, 1339.29, 160.71, 12.00, 1, 2),
(18, 46, 4, 1500.00, 1339.29, 160.71, 12.00, 1, 2),
(19, 47, 5, 800.00, 714.29, 85.71, 12.00, 1, 2),
(21, 49, 9, 5000.00, 4464.29, 535.71, 12.00, 1, 1),
(22, 50, 6, 1000.00, 892.86, 107.14, 12.00, 1, 1),
(23, 51, 7, 1200.00, 1071.43, 128.57, 12.00, 1, 1),
(24, 51, 2, 10000.00, 8928.57, 1071.43, 12.00, 1, 1),
(25, 52, 4, 1500.00, 1339.29, 160.71, 12.00, 1, 1),
(26, 53, 9, 5000.00, 4464.29, 535.71, 12.00, 1, 1),
(27, 54, 6, 1000.00, 892.86, 107.14, 12.00, 1, 1),
(28, 55, 7, 1200.00, 1071.43, 128.57, 12.00, 1, 1),
(29, 55, 4, 1500.00, 1339.29, 160.71, 12.00, 1, 1),
(30, 56, 2, 10000.00, 8928.57, 1071.43, 12.00, 1, 1),
(31, 57, 5, 800.00, 714.29, 85.71, 12.00, 1, 1),
(32, 57, 8, 45000.00, 40178.57, 4821.43, 12.00, 1, 1),
(33, 58, 8, 45000.00, 40178.57, 4821.43, 12.00, 1, 1),
(34, 59, 1, 800.00, 714.29, 85.71, 12.00, 1, 1),
(35, 59, 4, 1500.00, 1339.29, 160.71, 12.00, 1, 1),
(36, 60, 6, 1000.00, 892.86, 107.14, 12.00, 1, 1),
(37, 60, 1, 800.00, 714.29, 85.71, 12.00, 1, 1),
(38, 60, 6, 1000.00, 892.86, 107.14, 12.00, 1, 1),
(39, 61, 8, 45000.00, 40178.57, 4821.43, 12.00, 1, 1),
(40, 62, 1, 800.00, 714.29, 85.71, 12.00, 1, 1),
(41, 62, 9, 5000.00, 4464.29, 535.71, 12.00, 1, 1),
(42, 63, 4, 1500.00, 1339.29, 160.71, 12.00, 1, 1),
(43, 64, 5, 800.00, 714.29, 85.71, 12.00, 1, 1),
(44, 64, 6, 1000.00, 892.86, 107.14, 12.00, 1, 1),
(45, 65, 6, 1000.00, 892.86, 107.14, 12.00, 1, 1),
(46, 66, 9, 5000.00, 4464.29, 535.71, 12.00, 1, 1),
(47, 67, 8, 45000.00, 40178.57, 4821.43, 12.00, 1, 1),
(48, 68, 2, 10000.00, 8928.57, 1071.43, 12.00, 1, 1),
(49, 69, 6, 1500.00, 1339.29, 160.71, 12.00, 1, 1),
(50, 70, 8, 45000.00, 40178.57, 4821.43, 12.00, 1, 1),
(51, 71, 7, 1200.00, 1071.43, 128.57, 12.00, 1, 1),
(52, 72, 7, 1200.00, 1071.43, 128.57, 12.00, 1, 1),
(53, 72, 7, 1200.00, 1071.43, 128.57, 12.00, 1, 1),
(54, 73, 4, 1500.00, 1339.29, 160.71, 12.00, 1, 1),
(55, 74, 6, 1500.00, 1339.29, 160.71, 12.00, 1, 1),
(56, 75, 9, 5000.00, 4464.29, 535.71, 12.00, 1, 1),
(57, 76, 2, 10000.00, 8928.57, 1071.43, 12.00, 1, 1),
(58, 77, 2, 11200.00, 10000.00, 1200.00, 12.00, 1, 1),
(59, 78, 2, 11200.00, 10000.00, 1200.00, 12.00, 1, 1),
(60, 79, 16, 2000.00, 2000.00, 0.00, 12.00, 0, 1),
(61, 80, 17, 138.88, 124.00, 14.88, 12.00, 1, 1),
(62, 81, 18, 100.00, 100.00, 0.00, 12.00, 0, 1),
(63, 82, 16, 2000.00, 2000.00, 0.00, 12.00, 0, 1),
(64, 82, 17, 138.88, 124.00, 14.88, 12.00, 1, 1),
(65, 83, 7, 1344.00, 1200.00, 144.00, 12.00, 1, 1),
(66, 84, 9, 5600.00, 5000.00, 600.00, 12.00, 1, 1),
(67, 85, 2, 11200.00, 10000.00, 1200.00, 12.00, 1, 1),
(68, 86, 1, 896.00, 800.00, 96.00, 12.00, 1, 1),
(69, 87, 2, 11200.00, 10000.00, 1200.00, 12.00, 1, 1),
(70, 88, 14, 8960.00, 8000.00, 960.00, 12.00, 1, 1);

-- --------------------------------------------------------

--
-- Table structure for table `transactions`
--

CREATE TABLE `transactions` (
  `TransactionID` int(11) NOT NULL,
  `DentistID` int(11) NOT NULL,
  `StaffID` int(11) NOT NULL,
  `PatientID` int(11) NOT NULL,
  `TotalAmount` decimal(20,2) NOT NULL,
  `TransactionDate` date NOT NULL,
  `Notes` text DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `transactions`
--

INSERT INTO `transactions` (`TransactionID`, `DentistID`, `StaffID`, `PatientID`, `TotalAmount`, `TransactionDate`, `Notes`) VALUES
(37, 6, 3, 7, 800.00, '2025-12-12', NULL),
(38, 6, 3, 7, 10800.00, '2025-12-12', NULL),
(39, 6, 3, 7, 10000.00, '2025-12-12', NULL),
(40, 6, 3, 7, 10800.00, '2025-12-12', NULL),
(41, 6, 3, 8, 20000.00, '2025-12-13', NULL),
(42, 8, 3, 9, 4500.00, '2025-12-13', NULL),
(43, 8, 3, 12, 3800.00, '2025-12-13', NULL),
(44, 8, 3, 12, 1500.00, '2025-12-13', NULL),
(45, 8, 3, 11, 3000.00, '2025-12-13', NULL),
(46, 8, 3, 12, 3000.00, '2025-12-14', NULL),
(47, 8, 3, 9, 1600.00, '2025-12-14', NULL),
(49, 14, 3, 13, 5000.00, '2025-12-14', NULL),
(50, 17, 3, 14, 1000.00, '2025-12-14', NULL),
(51, 14, 3, 15, 11200.00, '2025-12-14', NULL),
(52, 15, 3, 16, 1500.00, '2025-12-14', NULL),
(53, 14, 3, 17, 5000.00, '2025-12-14', NULL),
(54, 17, 3, 18, 1000.00, '2025-12-14', NULL),
(55, 8, 3, 19, 2700.00, '2025-12-14', NULL),
(56, 17, 3, 19, 10000.00, '2025-12-14', NULL),
(57, 17, 3, 20, 45800.00, '2025-12-14', NULL),
(58, 8, 3, 21, 45000.00, '2025-12-14', NULL),
(59, 14, 3, 22, 2300.00, '2025-12-14', NULL),
(60, 15, 3, 23, 2800.00, '2025-12-14', NULL),
(61, 15, 3, 8, 45000.00, '2025-12-14', NULL),
(62, 14, 3, 7, 5800.00, '2025-12-14', NULL),
(63, 8, 16, 12, 1500.00, '2025-12-14', NULL),
(64, 17, 16, 24, 1800.00, '2025-12-14', NULL),
(65, 15, 3, 7, 1000.00, '2025-12-15', NULL),
(66, 6, 3, 23, 5000.00, '2025-12-15', NULL),
(67, 15, 3, 19, 45000.00, '2025-12-15', NULL),
(68, 14, 22, 19, 10000.00, '2025-12-15', NULL),
(69, 6, 3, 25, 1500.00, '2025-12-16', NULL),
(70, 17, 3, 9, 45000.00, '2025-12-16', NULL),
(71, 6, 3, 8, 1200.00, '2025-12-16', NULL),
(72, 8, 3, 23, 2400.00, '2025-12-16', NULL),
(73, 6, 3, 26, 1500.00, '2025-12-16', NULL),
(74, 17, 3, 26, 1500.00, '2025-12-16', NULL),
(75, 15, 3, 23, 5000.00, '2025-12-16', NULL),
(76, 6, 3, 23, 10000.00, '2025-12-16', 'Braces upper teeth'),
(77, 8, 3, 23, 11200.00, '2025-12-17', 'Braces bottom teeth'),
(78, 8, 3, 17, 11200.00, '2025-12-17', 'Brace top'),
(79, 15, 3, 17, 2000.00, '2025-12-17', 'test lang'),
(80, 15, 3, 17, 138.88, '2025-12-17', 'test lang again'),
(81, 15, 3, 17, 100.00, '2025-12-17', 'test no vat'),
(82, 15, 3, 26, 2138.88, '2025-12-17', 'another test haha'),
(83, 8, 3, 17, 1344.00, '2025-12-17', 'test lang'),
(84, 8, 3, 23, 5600.00, '2025-12-17', 'sample'),
(85, 8, 3, 23, 11200.00, '2025-12-17', 'braces top teeth'),
(86, 8, 3, 23, 896.00, '2025-12-17', 'test'),
(87, 8, 3, 25, 11200.00, '2025-12-18', 'Braces lower teeth'),
(88, 8, 3, 21, 8960.00, '2025-12-18', NULL);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `dentist`
--
ALTER TABLE `dentist`
  ADD PRIMARY KEY (`StaffID`),
  ADD UNIQUE KEY `LicenseNum` (`LicenseNum`);

--
-- Indexes for table `patient`
--
ALTER TABLE `patient`
  ADD PRIMARY KEY (`PatientID`);

--
-- Indexes for table `services`
--
ALTER TABLE `services`
  ADD PRIMARY KEY (`ServiceID`);

--
-- Indexes for table `staff`
--
ALTER TABLE `staff`
  ADD PRIMARY KEY (`StaffID`);

--
-- Indexes for table `staffcred`
--
ALTER TABLE `staffcred`
  ADD PRIMARY KEY (`StaffID`);

--
-- Indexes for table `transactiondetails`
--
ALTER TABLE `transactiondetails`
  ADD PRIMARY KEY (`TransactionDetailsID`),
  ADD KEY `TransactionID` (`TransactionID`),
  ADD KEY `ServiceID` (`ServiceID`);

--
-- Indexes for table `transactions`
--
ALTER TABLE `transactions`
  ADD PRIMARY KEY (`TransactionID`),
  ADD KEY `DentistID` (`DentistID`),
  ADD KEY `StaffID` (`StaffID`),
  ADD KEY `PatientID` (`PatientID`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `patient`
--
ALTER TABLE `patient`
  MODIFY `PatientID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=28;

--
-- AUTO_INCREMENT for table `services`
--
ALTER TABLE `services`
  MODIFY `ServiceID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=19;

--
-- AUTO_INCREMENT for table `staff`
--
ALTER TABLE `staff`
  MODIFY `StaffID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=28;

--
-- AUTO_INCREMENT for table `transactiondetails`
--
ALTER TABLE `transactiondetails`
  MODIFY `TransactionDetailsID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=71;

--
-- AUTO_INCREMENT for table `transactions`
--
ALTER TABLE `transactions`
  MODIFY `TransactionID` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=89;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `dentist`
--
ALTER TABLE `dentist`
  ADD CONSTRAINT `dentist_ibfk_1` FOREIGN KEY (`StaffID`) REFERENCES `staff` (`StaffID`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `staffcred`
--
ALTER TABLE `staffcred`
  ADD CONSTRAINT `staffcred_ibfk_1` FOREIGN KEY (`StaffID`) REFERENCES `staff` (`StaffID`) ON DELETE CASCADE ON UPDATE CASCADE;

--
-- Constraints for table `transactiondetails`
--
ALTER TABLE `transactiondetails`
  ADD CONSTRAINT `transactiondetails_ibfk_1` FOREIGN KEY (`TransactionID`) REFERENCES `transactions` (`TransactionID`) ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT `transactiondetails_ibfk_2` FOREIGN KEY (`ServiceID`) REFERENCES `services` (`ServiceID`) ON UPDATE CASCADE;

--
-- Constraints for table `transactions`
--
ALTER TABLE `transactions`
  ADD CONSTRAINT `transactions_ibfk_1` FOREIGN KEY (`DentistID`) REFERENCES `dentist` (`StaffID`) ON UPDATE CASCADE,
  ADD CONSTRAINT `transactions_ibfk_2` FOREIGN KEY (`StaffID`) REFERENCES `staff` (`StaffID`) ON UPDATE CASCADE,
  ADD CONSTRAINT `transactions_ibfk_3` FOREIGN KEY (`PatientID`) REFERENCES `patient` (`PatientID`) ON UPDATE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
