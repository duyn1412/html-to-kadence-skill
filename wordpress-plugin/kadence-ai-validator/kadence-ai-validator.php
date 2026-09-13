<?php
/**
 * Plugin Name: Kadence AI Validator
 * Description: REST endpoint for validating Kadence/Gutenberg block markup before publish (used by Cursor HTML-to-Kadence pipeline).
 * Version: 1.1.0
 * Author: Coast Residences
 * Requires at least: 6.0
 * Requires PHP: 7.4
 * Text Domain: kadence-ai-validator
 *
 * @package Kadence_AI_Validator
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

define( 'KADENCE_AI_VALIDATOR_VERSION', '1.1.0' );
define( 'KADENCE_AI_VALIDATOR_PATH', plugin_dir_path( __FILE__ ) );

require_once KADENCE_AI_VALIDATOR_PATH . 'includes/class-block-validator.php';
require_once KADENCE_AI_VALIDATOR_PATH . 'includes/class-kadence-rules.php';
require_once KADENCE_AI_VALIDATOR_PATH . 'includes/class-rest-controller.php';

add_action(
	'rest_api_init',
	static function () {
		Kadence_AI_Validator_REST_Controller::register_routes();
	}
);
