<?php
/*
 * Copyright (C) 2010-2012 Contrail consortium.
 *
 * This file is part of ConPaaS, an integrated runtime environment
 * for elastic cloud applications.
 *
 * ConPaaS is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 * ConPaaS is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with ConPaaS.  If not, see <http://www.gnu.org/licenses/>.
 */

require_module('ui/page');

class MysqlPage extends ServicePage {

	public function __construct(Service $service) {
		parent::__construct($service);
		$this->addJS('js/jquery.form.js');
		$this->addJS('js/mysql.js');
	}

	protected function renderApplicationAccess() {
		return '';
	}

	protected function renderInstanceActions() {
		return EditableTag()
			->setColor('orange')
			->setID('slaves')
			->setValue('0')
			->setText('MySQL slave');
	}

	private function renderFormRow($name, $details) {
		return
			'<div class="left-stack name">'.$name.'</div>'
			.'<div class="left-stack details">'.$details.'</div>'
			.'<div class="clear"></div>';
	}

	private function renderPasswordInput() {
		return
			'<div id="passwordForm" class="invisible">'
				.'<div class="left-stack name">new password</div>'
				.'<div class="left-stack details">'
					.'<input id="passwd" type="password" />'
					.'<b class="hint"> at least 8 characters</b>'
				.'</div>'
				.'<div class="clear"></div>'
				.'<div class="left-stack name">retype password</div>'
				.'<div class="left-stack details">'
					.'<input id="passwdRe" type="password" />'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>';
	}

	private function renderPasswordReset() {
		return $this->renderPasswordInput()
			.'<div id="resetPasswordForm" class="invisible">'
				.'<div class="left-stack name"></div>'
				.'<div class="left-stack details">'
					.'<input id="resetPassword" type="button" '
						.' value="reset password" />'
					.'<i id="resetStatus" class="invisible"></i>'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>';
	}

	private function renderCommand() {
		$users = $this->service->getUsers();
		$cmd = 'mysql -h '.$this->service->getMasterAddr()
			.' -u '.$users[0].' -p';
		return '<input class="command" type="text" readonly="readonly" '
			.' value="'.$cmd.'" title="shell command"/>'
			.'<b class="hint"> Click on command to Copy it</b>';
	}

	private function renderUsers() {
		$users = $this->service->getUsers();
		return $this->renderFormRow('user',
			'<span id="user">'.$users[0].'</span>');
	}

	public function renderAccessForm() {
		return
		'<div class="form-section mysql-access">'
			.'<div class="form-header">'
				.'<div class="title">'
					.'<img src="images/key.png"/>MySQL Access'
				.'</div>'
				.'<div class="access-box">'
					.'<a id="showResetPasswd" href="javascript: void(0);">'
						.'reset password'
					.'</a>'
					//.' &middot; <a href="javascript: void(0);">add user</a>'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>'
			.$this->renderFormRow('server address',
				$this->service->getAccessLocation())
			.$this->renderUsers()
			.$this->renderFormRow(
				'<img src="images/terminal.png" title="shell command" />',
				$this->renderCommand())
			.$this->renderPasswordReset()
		.'</div>';
	}

	public function renderLoadSection() {
		return
		'<div class="form-section mysql-load">'
			.'<div class="form-header">'
				.'<div class="title">'
					.'<img src="images/dbload.png"/>Load database from file'
				.'</div>'
				.'<div class="clear"></div>'
			.'</div>'
			.'<form id="loadform" action="ajax/dbload.php" '
				.'enctype="multipart/form-data">'
				.'<input id="dbfile" type="file" name="dbfile" />'
				.'<input id="loadfile" type="button" value="Load file" '
					.'disabled="disabled" />'
				.'<input type="hidden" name="sid" '
					.' value="'.$this->service->getSID().'" />'
				.'<img class="loading invisible" '
					.'src="images/icon_loading.gif"/>'
				.'<i class="positive invisible">File loaded successfully</i>'
				.'<i class="error invisible">Error loading file</i>'
			.'</form>'
		.'</div>';
	}

	public function renderContent() {
		$html = $this->renderInstancesSection();
		if ($this->service->isRunning()) {
			$html .= $this->renderAccessForm()
				.$this->renderLoadSection();
		}
		return $html;
	}
}

?>