<?php
/**
 * Validates Gutenberg block markup.
 *
 * @package Kadence_AI_Validator
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Parses, schema-checks, and render-tests block content.
 */
class Kadence_AI_Validator_Block_Validator {

	/** @var string[] Kadence attrs used in production but omitted from block.json schemas. */
	private static $kadence_extended_attrs = array(
		'kadenceAnimation',
		'kadenceAOSOptions',
		'kbVersion',
		'kadenceConditional',
		'kadenceBlock',
	);

	/** @var array<int, array<string, mixed>> */
	private $errors = array();

	/** @var array<int, array<string, mixed>> */
	private $warnings = array();

	/** @var int */
	private $block_count = 0;

	/** @var bool */
	private $strict = false;

	/** @var array<int, string> */
	private $render_issues = array();

	/**
	 * @param string $content Raw post content (block comments).
	 * @param bool   $strict  Treat warnings as errors.
	 * @return array<string, mixed>
	 */
	public function validate( $content, $strict = false ) {
		$this->errors        = array();
		$this->warnings      = array();
		$this->block_count   = 0;
		$this->strict        = (bool) $strict;
		$this->render_issues = array();

		if ( ! is_string( $content ) || '' === trim( $content ) ) {
			$this->errors[] = array(
				'block'   => '',
				'message' => 'Content is empty',
				'path'    => 'content',
			);
			return $this->build_response();
		}

		if ( ! function_exists( 'parse_blocks' ) ) {
			$this->errors[] = array(
				'block'   => '',
				'message' => 'parse_blocks() unavailable — WordPress block editor not loaded',
				'path'    => 'content',
			);
			return $this->build_response();
		}

		$blocks = parse_blocks( $content );

		if ( empty( $blocks ) ) {
			$this->errors[] = array(
				'block'   => '',
				'message' => 'No blocks parsed from content',
				'path'    => 'content',
			);
			return $this->build_response();
		}

		foreach ( $blocks as $index => $block ) {
			$this->validate_block( $block, "blocks[{$index}]" );
		}

		$this->validate_render( $content );

		return $this->build_response();
	}

	/**
	 * @param array  $block
	 * @param string $path
	 */
	private function validate_block( array $block, $path ) {
		$name = isset( $block['blockName'] ) ? $block['blockName'] : null;

		if ( empty( $name ) ) {
			$inner = isset( $block['innerHTML'] ) ? trim( $block['innerHTML'] ) : '';
			if ( '' !== $inner ) {
				$this->errors[] = array(
					'block'   => '(invalid)',
					'message' => 'Unrecoverable block — blockName is empty but innerHTML exists (classic HTML or corrupted block comment)',
					'path'    => $path,
				);
			}
			return;
		}

		$this->block_count++;

		$registry = WP_Block_Type_Registry::get_instance();

		if ( ! $registry->is_registered( $name ) ) {
			$this->errors[] = array(
				'block'   => $name,
				'message' => 'Block type is not registered — plugin may be inactive',
				'path'    => $path,
			);
		} else {
			$this->validate_attributes( $name, $block, $path, $registry->get_registered( $name ) );
		}

		$kadence = Kadence_AI_Validator_Kadence_Rules::validate( $block, $path );
		$this->errors   = array_merge( $this->errors, $kadence['errors'] );
		$this->warnings = array_merge( $this->warnings, $kadence['warnings'] );

		if ( ! empty( $block['innerBlocks'] ) && is_array( $block['innerBlocks'] ) ) {
			foreach ( $block['innerBlocks'] as $child_index => $child ) {
				$this->validate_block( $child, "{$path}.innerBlocks[{$child_index}]" );
			}
		}
	}

	/**
	 * @param string         $name
	 * @param array          $block
	 * @param string         $path
	 * @param WP_Block_Type  $block_type
	 */
	private function validate_attributes( $name, array $block, $path, $block_type ) {
		$attrs    = isset( $block['attrs'] ) && is_array( $block['attrs'] ) ? $block['attrs'] : array();
		$schema   = is_array( $block_type->attributes ) ? $block_type->attributes : array();
		$allowed  = array_keys( $schema );
		$skip     = array( 'lock', 'metadata' );

		foreach ( array_keys( $attrs ) as $key ) {
			if ( in_array( $key, $skip, true ) || 0 === strpos( $key, '__' ) ) {
				continue;
			}
			if ( in_array( $key, self::$kadence_extended_attrs, true ) ) {
				continue;
			}
			if ( ! in_array( $key, $allowed, true ) ) {
				$issue = array(
					'block'     => $name,
					'message'   => "Unknown attribute: {$key}",
					'path'      => $path,
					'attribute' => $key,
				);
				// Kadence saves extended attrs (AOS, kbVersion, etc.) not always listed in block.json.
				if ( 0 === strpos( $name, 'kadence/' ) ) {
					$this->warnings[] = $issue;
				} else {
					$this->errors[] = $issue;
				}
			}
		}

		foreach ( $attrs as $key => $value ) {
			if ( ! isset( $schema[ $key ] ) ) {
				continue;
			}
			$this->validate_attribute_type( $name, $key, $value, $schema[ $key ], $path );
		}
	}

	/**
	 * @param string $block_name
	 * @param string $key
	 * @param mixed  $value
	 * @param array  $def
	 * @param string $path
	 */
	private function validate_attribute_type( $block_name, $key, $value, array $def, $path ) {
		$type = isset( $def['type'] ) ? $def['type'] : null;
		if ( null === $type ) {
			return;
		}

		$valid = true;
		switch ( $type ) {
			case 'string':
				$valid = is_string( $value );
				break;
			case 'number':
			case 'integer':
				$valid = is_numeric( $value );
				break;
			case 'boolean':
				$valid = is_bool( $value );
				break;
			case 'array':
				$valid = is_array( $value );
				break;
			case 'object':
				$valid = is_array( $value );
				break;
		}

		if ( ! $valid ) {
			$this->errors[] = array(
				'block'     => $block_name,
				'message'   => "Attribute {$key} must be of type {$type}",
				'path'      => $path,
				'attribute' => $key,
			);
		}
	}

	/**
	 * Render full content and capture PHP warnings/notices.
	 *
	 * @param string $content
	 */
	private function validate_render( $content ) {
		if ( ! function_exists( 'do_blocks' ) ) {
			$this->warnings[] = array(
				'block'   => '',
				'message' => 'do_blocks() unavailable — skipped render test',
				'path'    => 'render',
			);
			return;
		}

		$captured = array();

		$handler = static function ( $errno, $errstr, $errfile, $errline ) use ( &$captured ) {
			$captured[] = array(
				'errno'   => $errno,
				'message' => $errstr,
				'file'    => $errfile,
				'line'    => $errline,
			);
			return true;
		};

		set_error_handler( $handler ); // phpcs:ignore WordPress.PHP.DevelopmentFunctions.error_log_set_error_handler

		try {
			$output = do_blocks( $content );
		} catch ( Throwable $e ) { // phpcs:ignore Generic.CodeAnalysis.EmptyStatement.DetectedCatch
			$this->errors[] = array(
				'block'   => '',
				'message' => 'Render exception: ' . $e->getMessage(),
				'path'    => 'render',
			);
			$output = '';
		}

		restore_error_handler();

		foreach ( $captured as $issue ) {
			$level = E_WARNING === $issue['errno'] || E_USER_WARNING === $issue['errno'] ? 'warning' : 'error';
			$entry = array(
				'block'   => '',
				'message' => 'PHP ' . $level . ' during render: ' . $issue['message'],
				'path'    => 'render',
				'file'    => basename( $issue['file'] ),
				'line'    => $issue['line'],
			);
			if ( 'warning' === $level ) {
				$this->warnings[] = $entry;
			} else {
				$this->errors[] = $entry;
			}
		}

		if ( '' === trim( (string) $output ) && $this->block_count > 0 ) {
			$this->warnings[] = array(
				'block'   => '',
				'message' => 'Render produced empty HTML — verify block inner content and attributes',
				'path'    => 'render',
			);
		}
	}

	/**
	 * @return array<string, mixed>
	 */
	private function build_response() {
		$errors   = $this->normalize_issues( $this->errors );
		$warnings = $this->normalize_issues( $this->warnings );

		if ( $this->strict ) {
			$errors = array_merge( $errors, $warnings );
			$warnings = array();
		}

		return array(
			'success'     => empty( $errors ),
			'block_count' => $this->block_count,
			'errors'      => $errors,
			'warnings'    => $warnings,
		);
	}

	/**
	 * @param array<int, array<string, mixed>> $issues
	 * @return array<int, array<string, mixed>>
	 */
	private function normalize_issues( array $issues ) {
		$normalized = array();
		foreach ( $issues as $issue ) {
			$row = array(
				'block'   => isset( $issue['block'] ) ? (string) $issue['block'] : '',
				'message' => isset( $issue['message'] ) ? (string) $issue['message'] : '',
			);
			if ( ! empty( $issue['path'] ) ) {
				$row['path'] = (string) $issue['path'];
			}
			if ( ! empty( $issue['attribute'] ) ) {
				$row['attribute'] = (string) $issue['attribute'];
			}
			$normalized[] = $row;
		}
		return $normalized;
	}
}
