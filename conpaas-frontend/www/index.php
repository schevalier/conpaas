<?php
/*
 * Copyright (C) 2010-2011 Contrail consortium.
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

require_once('__init__.php');
require_module('logging');
require_module('service');
require_module('service/factory');
require_module('ui/page/dashboard');
require_module('ui/service');

$page = new Dashboard();
$services = ServiceData::getServicesByUser($page->getUID());
?>
<?php echo $page->renderDoctype(); ?>
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
  	<?php echo $page->renderContentType(); ?>
    <?php echo $page->renderTitle(); ?>
    <?php echo $page->renderIcon(); ?>
    <?php echo $page->renderHeaderCSS(); ?>
  </head>
  <body class="<?php echo $page->getBrowserClass(); ?>">
	<?php echo $page->renderHeader(); ?>
  	<div class="pagecontent">
  		<div class="pageheader">
  			<?php echo $page->renderPageHeader(); ?>
  		</div>
  		<div id="servicesWrapper">
  		</div>
  	</div>
  	<?php echo $page->renderFooter(); ?>
  	<?php echo $page->renderJSLoad(); ?>
  </body>
</html>