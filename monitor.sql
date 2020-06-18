/*
Navicat MySQL Data Transfer

Source Server         : localhost
Source Server Version : 50638
Source Host           : localhost:3306
Source Database       : monitor

Target Server Type    : MYSQL
Target Server Version : 50638
File Encoding         : 65001

Date: 2020-06-15 09:40:57
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for `connect`
-- ----------------------------
DROP TABLE IF EXISTS `connect`;
CREATE TABLE `connect` (
  `ip` varchar(64) NOT NULL DEFAULT '',
  `send` int(10) DEFAULT '0',
  `start_time` datetime DEFAULT NULL,
  `end_time` datetime DEFAULT NULL,
  PRIMARY KEY (`ip`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of connect
-- ----------------------------
INSERT INTO `connect` VALUES ('127.0.0.1', '0', null, null);

-- ----------------------------
-- Table structure for `cpu`
-- ----------------------------
DROP TABLE IF EXISTS `cpu`;
CREATE TABLE `cpu` (
  `ip` varchar(64) NOT NULL DEFAULT '',
  `send` int(10) DEFAULT '0',
  `start_time` datetime DEFAULT NULL,
  `end_time` datetime DEFAULT NULL,
  PRIMARY KEY (`ip`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of cpu
-- ----------------------------
INSERT INTO `cpu` VALUES ('127.0.0.1', '0', null, null);

-- ----------------------------
-- Table structure for `disk`
-- ----------------------------
DROP TABLE IF EXISTS `disk`;
CREATE TABLE `disk` (
  `ip` varchar(64) NOT NULL DEFAULT '',
  `send` int(10) DEFAULT '0',
  `start_time` datetime DEFAULT NULL,
  `end_time` datetime DEFAULT NULL,
  PRIMARY KEY (`ip`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of disk
-- ----------------------------
INSERT INTO `disk` VALUES ('127.0.0.1', '0', null, null);

-- ----------------------------
-- Table structure for `info`
-- ----------------------------
DROP TABLE IF EXISTS `info`;
CREATE TABLE `info` (
  `ip` varchar(64) NOT NULL,
  `system_info` varchar(255) DEFAULT NULL,
  `phone` varchar(64) DEFAULT NULL,
  `open` int(1) NOT NULL DEFAULT '1',
  `port` int(10) DEFAULT NULL,
  `user` varchar(64) NOT NULL,
  `password` varchar(64) NOT NULL,
  `remote_port` int(10) NOT NULL,
  `mail` varchar(64) DEFAULT NULL,
  `wx` varchar(64) DEFAULT NULL,
  PRIMARY KEY (`ip`,`remote_port`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of info
-- ----------------------------
INSERT INTO `info` VALUES ('127.0.0.1', '监控系统名', null, '1', null, 'centos', 'password', '22', null, 'default');

-- ----------------------------
-- Table structure for `mem`
-- ----------------------------
DROP TABLE IF EXISTS `mem`;
CREATE TABLE `mem` (
  `ip` varchar(64) NOT NULL DEFAULT '',
  `send` int(10) DEFAULT '0',
  `start_time` datetime DEFAULT NULL,
  `end_time` datetime DEFAULT NULL,
  PRIMARY KEY (`ip`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of mem
-- ----------------------------
INSERT INTO `mem` VALUES ('127.0.0.1', '0', null, null);

-- ----------------------------
-- Table structure for `speed`
-- ----------------------------
DROP TABLE IF EXISTS `speed`;
CREATE TABLE `speed` (
  `ip` varchar(64) NOT NULL DEFAULT '',
  `send` int(10) DEFAULT '0',
  `start_time` datetime DEFAULT NULL,
  `end_time` datetime DEFAULT NULL,
  PRIMARY KEY (`ip`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of speed
-- ----------------------------
INSERT INTO `speed` VALUES ('127.0.0.1', '0', null, null);

-- ----------------------------
-- Table structure for `switch`
-- ----------------------------
DROP TABLE IF EXISTS `switch`;
CREATE TABLE `switch` (
  `ip` varchar(64) NOT NULL DEFAULT '',
  `cpu` int(10) DEFAULT '1',
  `mem` int(10) DEFAULT '1',
  `disk` int(10) DEFAULT '1',
  `speed` int(10) DEFAULT '1',
  `connect` int(10) DEFAULT '1',
  PRIMARY KEY (`ip`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of switch
-- ----------------------------
INSERT INTO `switch` VALUES ('127.0.0.1', '1', '1', '1', '1', '1');

-- ----------------------------
-- Table structure for `threshold`
-- ----------------------------
DROP TABLE IF EXISTS `threshold`;
CREATE TABLE `threshold` (
  `ip` varchar(64) NOT NULL,
  `cpu` int(10) NOT NULL DEFAULT '80',
  `mem` int(10) NOT NULL DEFAULT '90',
  `disk` int(10) NOT NULL DEFAULT '90',
  `speed` int(10) NOT NULL DEFAULT '1200000',
  `connect` int(10) NOT NULL DEFAULT '800',
  PRIMARY KEY (`ip`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of threshold
-- ----------------------------
INSERT INTO `threshold` VALUES ('127.0.0.1', '80', '90', '90', '1200000', '800');

-- ----------------------------
-- Table structure for `wx`
-- ----------------------------
DROP TABLE IF EXISTS `wx`;
CREATE TABLE `wx` (
  `name` varchar(64) NOT NULL,
  `webhook` varchar(255) NOT NULL,
  `initiative` int(10) NOT NULL DEFAULT '0',
  PRIMARY KEY (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Records of wx
-- ----------------------------
INSERT INTO `wx` VALUES ('default', '', '0');
