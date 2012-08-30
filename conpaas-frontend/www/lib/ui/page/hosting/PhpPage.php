<?php
/*
 * Copyright (c) 2010-2012, Contrail consortium.
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms,
 * with or without modification, are permitted provided
 * that the following conditions are met:
 *
 *  1. Redistributions of source code must retain the
 *     above copyright notice, this list of conditions
 *     and the following disclaimer.
 *  2. Redistributions in binary form must reproduce
 *     the above copyright notice, this list of
 *     conditions and the following disclaimer in the
 *     documentation and/or other materials provided
 *     with the distribution.
 *  3. Neither the name of the Contrail consortium nor the
 *     names of its contributors may be used to endorse
 *     or promote products derived from this software
 *     without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND
 * CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
 * INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
 * MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
 * DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
 * SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
 * BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
 * SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
 * INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
 * WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
 * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT
 * OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
 * POSSIBILITY OF SUCH DAMAGE.
 */

class PhpPage extends HostingPage {

	private function renderSettingsRow($description, $input) {
		return
			'<tr>'
				.'<td class="description">'.$description.'</td>'
				.'<td class="input">'.$input.'</td>'
			.'</tr>';
	}

	private function renderSwVersionInput() {
		return
		'<select onchange="confirm(\'Are you sure you want to change the '
			.' software version?\')">'
	  		.'<option>5.3</option>'
	  	.'</select>';
	}

	private function getCurrentExecLimit() {
		$conf = $this->service->getConfiguration();
		if ($conf === null || !isset($conf->phpconf->max_execution_time)) {
			// default value
			return 30;
		}
		return intval($conf->phpconf->max_execution_time);
	}

	public function renderExecTimeOptions() {
		static $options = array(30, 60, 90);
		$selected = $this->getCurrentExecLimit();
		$html = '<select id="conf-maxexec">';
		foreach ($options as $option) {
			$selectedField = $selected == $option ?
				'selected="selected"' : '';
			$html .= '<option value="'.$option.'" '.$selectedField.'>'
				.$option.' seconds</option>';
		}
		$html .= '</select>';
		return $html;
	}

	private function getCurrentMemLimit() {
		$conf = $this->service->getConfiguration();
		if ($conf === null || !isset($conf->phpconf->memory_limit)) {
			// default value
			return '128M';
		}
		return $conf->phpconf->memory_limit;
	}

	public function renderMemLimitOptions() {
		static $options = array('64M', '128M', '256M');
		$selected = $this->getCurrentMemLimit();
		$html = '<select id="conf-memlim">';
		foreach ($options as $option) {
			$selectedField = $selected == $option ?
				'selected="selected"' : '';
			$html .= '<option value="'.$option.'" '.$selectedField.'>'
				.$option.'</option>';
		}
		$html .= '</select>';
		return $html;
	}

	public function renderSettingsSection() {
		return
		'<div class="form-section">'
			.'<div class="form-header">'
				.'<div class="title">Settings</div>'
				.'<div class="clear"></div>'
			.'</div>'
			.'<table class="form settings-form">'
				.$this->renderSettingsRow('Software Version ',
					$this->renderSwVersionInput())
				.$this->renderSettingsRow('Maximum script execution time',
					$this->renderExecTimeOptions())
				.$this->renderSettingsRow('Memory limit',
					$this->renderMemLimitOptions())
				.'<tr><td class="description"></td>'
					.'<td class="input actions">'
					.'<input id="saveconf" type="button" disabled="disabled" '
						.'value="save" />'
					 .'<i class="positive invisible">Submitted successfully</i>'
					.'</td>'
				.'</tr>'
			.'</table>'
		.'</div>';
	}

	private function renderCdsForm() {
		if ($this->service->isCdnEnabled()) {
			return
			'Content delivery is <b>ON</b> using '
			.'<b>'.$this->service->getCds()->getName().'</b>. '
			.'You should be able to get the following variables into your application:'
			.'<div class="code">'
				.'<b class="line" title="url prefix for offloaded content">'
					.'$_SERVER[\'CDN_URL_PREFIX\']'
				.'</b>'
				.'<b class="line" title="country of the remote address">'
					.'$_SERVER[\'GEOIP_COUNTRY_CODE\']'
				.'</b>'
			.'</div>';
		}
		$cdsServices = $this->service->getAvailableCds($this->getUID());
		$options = '';
		$subscribeButton = InputButton('subscribe')->setId('cds_subscribe');
		if (count($cdsServices) > 0) {
			foreach ($cdsServices as $cds) {
				$options .= '<option value="'.$cds->getSID().'">'
					.$cds->getName().'</option>';
			}
		} else {
			$options = '<option>No available CDS</option>';
			$subscribeButton->setDisabled(true);
		}
		// we cannot subscribe to a CDS if we are not running, because we don't
		// have an origin address yet
		if (!$this->service->isRunning()) {
			$subscribeButton
				->setDisabled(true)
				->setTitle('the service must be running');
		}
		return
		'Content delivery is <b>OFF</b>. To be able to offload static content '
		.'you may want to subscribe to one of the available CDN services.'
		.'<div class="subscribe-form">'
			.'<select id="cds">'.$options.'</select> '
			.$subscribeButton.' '
			.'<img id="subscribe-loading" class="invisible" src="images/icon_loading.gif" />'
		.'</div>';
	}

	public function renderCdsStatus() {
		if ($this->service->isCdnEnabled()) {
			return
			InputButton('unsubscribe')->setId('cds_unsubscribe')
			.'<img class="led" src="images/ledgreen.png" '
				.'title="Content Delivery is ON" /> ';
		}
		return '<img class="led" src="images/ledorange.png" '
			.'title="Content Delivery is OFF"/>';
	}

	public function renderCdsSection() {
		return '';
        /*
		'<div class="form-section">'
			.'<div class="form-header">'
				.''
				.'<div class="title">'
					.'<img src="images/cds.png" width="23"/><i>Content Delivery</i>'
				.'</div>'
				.'<div class="access-box">'
					.$this->renderCdsStatus()
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>'
			.'<div class="cds-subscribe">'
				.$this->renderCdsForm()
			.'</div>'
		.'</div>';
       */
	}

	public function renderContent() {
		return $this->renderInstancesSection()
			.$this->renderCdsSection()
			.$this->renderCodeSection()
			.$this->renderSettingsSection();
	}
}
