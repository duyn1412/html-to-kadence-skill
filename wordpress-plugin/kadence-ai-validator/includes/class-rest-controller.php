<?php
/**
 * REST API controller.
 *
 * @package Kadence_AI_Validator
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Registers kadence-ai/v1 routes.
 */
class Kadence_AI_Validator_REST_Controller {

	const REST_NAMESPACE = 'kadence-ai/v1';

	/**
	 * Register routes.
	 */
	public static function register_routes() {
		register_rest_route(
			self::REST_NAMESPACE,
			'/validate',
			array(
				array(
					'methods'             => WP_REST_Server::CREATABLE,
					'callback'            => array( __CLASS__, 'validate_content' ),
					'permission_callback' => array( __CLASS__, 'can_validate' ),
					'args'                => array(
						'content' => array(
							'required'          => true,
							'type'              => 'string',
							'sanitize_callback' => static function ( $value ) {
								// Preserve Gutenberg block comments — do not use wp_kses_post.
								return is_string( $value ) ? wp_unslash( $value ) : '';
							},
							'validate_callback' => static function ( $value ) {
								return is_string( $value ) && '' !== trim( $value );
							},
						),
						'strict'  => array(
							'required' => false,
							'type'     => 'boolean',
							'default'  => false,
						),
					),
				),
				array(
					'methods'             => WP_REST_Server::READABLE,
					'callback'            => array( __CLASS__, 'health_check' ),
					'permission_callback' => array( __CLASS__, 'can_validate' ),
				),
			)
		);
	}

	/**
	 * @return bool
	 */
	public static function can_validate() {
		return current_user_can( 'edit_posts' );
	}

	/**
	 * POST /kadence-ai/v1/validate
	 *
	 * @param WP_REST_Request $request Request.
	 * @return WP_REST_Response
	 */
	public static function validate_content( WP_REST_Request $request ) {
		$content = (string) $request->get_param( 'content' );
		$strict  = (bool) $request->get_param( 'strict' );

		$validator = new Kadence_AI_Validator_Block_Validator();
		$result    = $validator->validate( $content, $strict );

		$result['plugin_version'] = KADENCE_AI_VALIDATOR_VERSION;
		$result['validated_at']   = gmdate( 'c' );

		$status = ! empty( $result['success'] ) ? 200 : 422;

		return new WP_REST_Response( $result, $status );
	}

	/**
	 * GET /kadence-ai/v1/validate — health / capability check.
	 *
	 * @return WP_REST_Response
	 */
	public static function health_check() {
		$registry = WP_Block_Type_Registry::get_instance();
		$kadence  = 0;

		foreach ( $registry->get_all_registered() as $name => $type ) {
			if ( 0 === strpos( $name, 'kadence/' ) ) {
				$kadence++;
			}
		}

		return new WP_REST_Response(
			array(
				'status'               => 'ok',
				'plugin_version'       => KADENCE_AI_VALIDATOR_VERSION,
				'kadence_blocks_count' => $kadence,
				'endpoint'             => rest_url( self::REST_NAMESPACE . '/validate' ),
			),
			200
		);
	}
}
