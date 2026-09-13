<?php
/**
 * Coast / Kadence-specific validation rules beyond block.json schema.
 *
 * @package Kadence_AI_Validator
 */

if ( ! defined( 'ABSPATH' ) ) {
	exit;
}

/**
 * Kadence domain rules learned from live Coast markup failures.
 */
class Kadence_AI_Validator_Kadence_Rules {

	/** @var string[] Kadence global font-size variable slugs (editor + frontend). */
	private static $font_size_variable_tokens = array(
		'sm',
		'base_sub',
		'md',
		'lg',
		'xl',
		'xxl',
		'3xl',
	);

	/**
	 * Run Kadence-specific checks on a parsed block.
	 *
	 * @param array  $block      Parsed block from parse_blocks().
	 * @param string $block_path Human-readable block path.
	 * @return array{errors: array<int, array<string, mixed>>, warnings: array<int, array<string, mixed>>}
	 */
	public static function validate( array $block, $block_path ) {
		$errors   = array();
		$warnings = array();
		$name     = isset( $block['blockName'] ) ? (string) $block['blockName'] : '';
		$attrs    = isset( $block['attrs'] ) && is_array( $block['attrs'] ) ? $block['attrs'] : array();

		if ( 0 !== strpos( $name, 'kadence/' ) ) {
			return compact( 'errors', 'warnings' );
		}

		if ( empty( $attrs['uniqueID'] ) ) {
			$errors[] = self::issue(
				$name,
				'Missing required attribute: uniqueID',
				$block_path,
				'uniqueID'
			);
		} elseif ( ! is_string( $attrs['uniqueID'] ) ) {
			$errors[] = self::issue(
				$name,
				'Attribute uniqueID must be a string',
				$block_path,
				'uniqueID'
			);
		}

		if ( 'kadence/advancedheading' === $name ) {
			self::validate_advanced_heading( $block, $block_path, $errors, $warnings );
		}

		if ( 'kadence/rowlayout' === $name ) {
			self::validate_row_layout( $attrs, $block_path, $errors, $warnings );
		}

		if ( 'kadence/image' === $name ) {
			self::validate_image( $attrs, $block_path, $errors, $warnings );
		}

		if ( isset( $attrs['overlay'] ) && is_string( $attrs['overlay'] ) && 0 === strpos( $attrs['overlay'], 'palette' ) ) {
			$warnings[] = self::issue(
				$name,
				'Row overlay should use hex color (e.g. #071e1c), not palette slug — may not render correctly',
				$block_path,
				'overlay'
			);
		}

		if ( isset( $attrs['fontSize'] ) ) {
			self::validate_font_size_attr( $name, $attrs['fontSize'], $block_path, $errors );
		}

		return compact( 'errors', 'warnings' );
	}

	/**
	 * Advanced Heading: verify saved inner HTML matches what Kadence save() emits.
	 * Mismatches here are exactly what makes Gutenberg flag "invalid block".
	 *
	 * @param array  $block      Full parsed block (attrs + innerHTML).
	 * @param string $block_path
	 * @param array  $errors
	 * @param array  $warnings
	 */
	private static function validate_advanced_heading( array $block, $block_path, array &$errors, array &$warnings ) {
		$attrs = isset( $block['attrs'] ) && is_array( $block['attrs'] ) ? $block['attrs'] : array();
		$inner = isset( $block['innerHTML'] ) ? (string) $block['innerHTML'] : '';
		$uid   = isset( $attrs['uniqueID'] ) ? (string) $attrs['uniqueID'] : '';

		if ( '' === trim( $inner ) ) {
			$errors[] = self::issue(
				'kadence/advancedheading',
				'Empty inner HTML — heading must contain the rendered tag (h1-h6/p/span)',
				$block_path
			);
			return;
		}

		if ( '' !== $uid ) {
			if ( false === strpos( $inner, 'kt-adv-heading' . $uid ) ) {
				$errors[] = self::issue(
					'kadence/advancedheading',
					"Inner HTML missing class kt-adv-heading{$uid} — editor will mark block invalid",
					$block_path
				);
			}
			if ( false === strpos( $inner, 'data-kb-block="kb-adv-heading' . $uid . '"' ) ) {
				$errors[] = self::issue(
					'kadence/advancedheading',
					"Inner HTML missing data-kb-block=\"kb-adv-heading{$uid}\" — editor will mark block invalid",
					$block_path
				);
			}
		}

		// colorClass (e.g. theme-palette7) must be reflected as has-theme-palette-7-color has-text-color.
		if ( ! empty( $attrs['colorClass'] ) && is_string( $attrs['colorClass'] ) ) {
			$expected = 'has-' . preg_replace( '/(\d+)$/', '-$1', $attrs['colorClass'] ) . '-color';
			if ( false === strpos( $inner, $expected ) ) {
				$errors[] = self::issue(
					'kadence/advancedheading',
					"colorClass \"{$attrs['colorClass']}\" set but inner HTML missing class \"{$expected} has-text-color\" — editor will mark block invalid",
					$block_path,
					'colorClass'
				);
			} elseif ( false === strpos( $inner, 'has-text-color' ) ) {
				$errors[] = self::issue(
					'kadence/advancedheading',
					'colorClass set but inner HTML missing has-text-color class — editor will mark block invalid',
					$block_path,
					'colorClass'
				);
			}
		}

		// link attribute wraps content in an anchor — attrs without markup invalidate the block.
		if ( ! empty( $attrs['link'] ) && false === stripos( $inner, '<a ' ) ) {
			$errors[] = self::issue(
				'kadence/advancedheading',
				'link attribute set but inner HTML contains no <a> tag — remove attribute or use inline anchor in content',
				$block_path,
				'link'
			);
		}

		// AOS animation attrs must be mirrored in the saved HTML.
		if ( ! empty( $attrs['kadenceAnimation'] ) && false === strpos( $inner, 'data-aos=' ) ) {
			$warnings[] = self::issue(
				'kadence/advancedheading',
				'kadenceAnimation set but inner HTML missing data-aos attribute',
				$block_path,
				'kadenceAnimation'
			);
		}

		// Tag consistency: htmlTag/level must match the rendered element.
		$html_tag = isset( $attrs['htmlTag'] ) ? (string) $attrs['htmlTag'] : '';
		$level    = isset( $attrs['level'] ) ? (int) $attrs['level'] : 2;
		$expected_tag = in_array( $html_tag, array( 'p', 'span', 'div' ), true ) ? $html_tag : 'h' . $level;
		if ( ! preg_match( '/<' . preg_quote( $expected_tag, '/' ) . '[\s>]/i', $inner ) ) {
			$errors[] = self::issue(
				'kadence/advancedheading',
				"Attributes expect <{$expected_tag}> but inner HTML uses a different tag — editor will mark block invalid",
				$block_path
			);
		}
	}

	/**
	 * @param array  $attrs
	 * @param string $block_path
	 * @param array  $errors
	 * @param array  $warnings
	 */
	private static function validate_row_layout( array $attrs, $block_path, array &$errors, array &$warnings ) {
		$columns = isset( $attrs['columns'] ) ? (int) $attrs['columns'] : 1;

		if ( $columns > 1 && empty( $attrs['colLayout'] ) ) {
			$warnings[] = self::issue(
				'kadence/rowlayout',
				'Multi-column row should define colLayout',
				$block_path,
				'colLayout'
			);
		}

		if ( ! empty( $attrs['bgImg'] ) && is_string( $attrs['bgImg'] ) && false !== stripos( $attrs['bgImg'], 'REPLACE_MEDIA' ) ) {
			$errors[] = self::issue(
				'kadence/rowlayout',
				'Placeholder bgImg URL detected — upload media and use a real URL',
				$block_path,
				'bgImg'
			);
		}

		if ( ! empty( $attrs['bgColor'] ) && empty( $attrs['bgColorClass'] ) && 0 === strpos( (string) $attrs['bgColor'], 'palette' ) ) {
			$warnings[] = self::issue(
				'kadence/rowlayout',
				'Missing bgColorClass for palette background — Coast pages use theme-paletteN classes',
				$block_path,
				'bgColorClass'
			);
		}
	}

	/**
	 * @param array  $attrs
	 * @param string $block_path
	 * @param array  $errors
	 * @param array  $warnings
	 */
	private static function validate_image( array $attrs, $block_path, array &$errors, array &$warnings ) {
		if ( ! empty( $attrs['url'] ) && is_string( $attrs['url'] ) && false !== stripos( $attrs['url'], 'REPLACE_MEDIA' ) ) {
			$errors[] = self::issue(
				'kadence/image',
				'Placeholder image URL detected — upload media and use id + real URL',
				$block_path,
				'url'
			);
		}

		if ( empty( $attrs['id'] ) && empty( $attrs['url'] ) ) {
			$errors[] = self::issue(
				'kadence/image',
				'Image block missing both id and url',
				$block_path,
				'id'
			);
		}

		if ( isset( $attrs['imageRatio'] ) ) {
			$warnings[] = self::issue(
				'kadence/image',
				'Unknown attribute: imageRatio — use ratio + useRatio (Coast live pattern)',
				$block_path,
				'imageRatio'
			);
		}
	}

	/**
	 * @param string $block_name
	 * @param mixed  $font_size
	 * @param string $block_path
	 * @param array  $errors
	 */
	private static function validate_font_size_attr( $block_name, $font_size, $block_path, array &$errors ) {
		if ( ! is_array( $font_size ) ) {
			return;
		}

		foreach ( $font_size as $value ) {
			if ( null === $value || '' === $value ) {
				continue;
			}
			if ( is_string( $value ) && in_array( $value, self::$font_size_variable_tokens, true ) ) {
				continue;
			}
			if ( is_string( $value ) && ! is_numeric( $value ) ) {
				$errors[] = self::issue(
					$block_name,
					"fontSize value \"{$value}\" must be numeric px or a Kadence size token (sm, base_sub, md, lg, xl, xxl, 3xl)",
					$block_path,
					'fontSize'
				);
			}
		}
	}

	/**
	 * @param string      $block
	 * @param string      $message
	 * @param string      $block_path
	 * @param string|null $attribute
	 * @return array<string, mixed>
	 */
	private static function issue( $block, $message, $block_path, $attribute = null ) {
		$issue = array(
			'block'   => $block,
			'message' => $message,
			'path'    => $block_path,
		);
		if ( null !== $attribute ) {
			$issue['attribute'] = $attribute;
		}
		return $issue;
	}
}
