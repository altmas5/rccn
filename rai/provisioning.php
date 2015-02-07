<?php 
require_once('modules/subscriber.php');
require_once('modules/configuration.php');
require_once('include/menu.php'); 
require_once('include/header.php');

print_menu('subscribers');
 
?>	

<br/><br/><br/><br/>

<?php


function print_form($post_data,$errors) {

	$firstname = ($_POST['firstname'] != '') ? $_POST['firstname'] : '';
	$callerid = ($_POST['callerid'] != '') ? $_POST['callerid'] : '';
	$amount = ($_POST['amount'] != '') ? $_POST['amount'] : '0';
	$location = ($_POST['location'] != '') ? $_POST['location'] : '';

	

?>
			<div id="stylized" class="myform">
				<form id="form" name="form" method="post" action="provisioning.php">
				<h1><?= _("Provision a new subscriber") ?></h1><br/>
<?php
				// get imsi
				$imsi = shell_exec("/var/rhizomatica/bin/get_imsi.py");
				if (isset($imsi) && strlen($imsi) == 16) {
					echo "&nbsp;&nbsp;Got IMSI: $imsi";
				} else {
					echo "&nbsp;&nbsp;Error getting IMSI please retry";
				}

				$sub = new Subscriber();
                                try {
                                	$ext = $sub->get_extension($imsi);
				} catch (SubscriberException $e) { 
					echo "&nbsp;&nbsp;Error getting Subscriber extension";
				}

?>
				<br/>
				<span style='color: red; font-size: 12px;'><?= $errors ?></span><br/>
                                <label><?= _("Name") ?>
                                <span class="small"><?= _("Subscriber Name") ?></span>
                                </label>
                                <input type="text" name="firstname" id="firstname" value="<?=$firstname?>"/>

				<label><?= _("Subscriber number") ?>
				<span class="small"><?= _("Subscriber number") ?></span>
				</label>
				<input type="text" name="callerid" id="callerid" value="<?=$ext?>"/>

				<label><?= _("Location") ?>
				<span class="small"><?= _("Subscriber location") ?></span>
				</label>
				<input type="text" name="location" id="location" value="<?=$location?>"/>
				
				<label><?= _("Initial Balance") ?>
				<span class="small"><?= _("Amount to add") ?></span>
				</label>
				<input type="text" name="amount" id="amount" value="<?=$amount?>"/><br/>
			
				<button type="submit" name="add_subscriber"><?= _("Add") ?></button>
				<div class="spacer"></div>
				</form>
			</div>
<?
}	
				$error_txt = "";
				// errors check
				if (isset($_POST['add_subscriber'])) {
					// form pressed verify if any data is missing
					$firstname = $_POST['firstname'];
					$callerid = $_POST['callerid'];
					$amount = $_POST['amount'];
					$location = $_POST['location'];

					if ($firstname == "") {
						$error_txt .= _("Name is empty")."<br/>";
					}
					if ($callerid == "" || strlen($callerid) > 5 || strlen($callerid) < 5) {
						$error_txt .= _("Subscriber number is invalid")."<br/>";
					}
					if ($amount == "") {
						$error_txt .= _("Initial balance is empty")."<br/>";
					}
					//if ($location == "") {
					//	$error_txt .= _("Location is empty");
					//}
				} 

				if (isset($_POST['add_subscriber']) && $error_txt != "") {
					print_form(1,$error_txt);
				}elseif (isset($_POST['add_subscriber']) && $error_txt == "") {
					// no error process form
		                        
					$firstname = $_POST['firstname'];
                                        $callerid = $_POST['callerid'];
                                        $amount = $_POST['amount'];
					$location = $_POST['location'];

					// get internal prefix
					$site = new Configuration();
					$info = $site->getSite();
					$internalprefix = $info->postcode.$info->pbxcode;

					$new_num = "$internalprefix$callerid";
				
					echo "<center>";
					
					$sub = new Subscriber();
					try {
						$sub->set("",$callerid,$firstname,1,$amount,"", $location);
						$ret = $sub->create();
						echo "<img src='img/true.png' width='200' height='170' /><br/><br/>";
						if ($ret != "") {
							echo "<span style='font-size: 20px;'>"._("Subscriber already exists! New subscriber number").": <b>$ret</b> "._("Successfully provisioned with an initial balance of")." $amount<br/><br/>";
						} else {
							echo "<span style='font-size: 20px;'>"._("Subscriber number").": <b>$callerid</b> "._("Successfully provisioned with an initial balance of")." $amount<br/><br/>";
						}
						echo "<a href='provisioning.php'><button class='b1'>"._("Go Back")."</button></a>";
					} catch (SubscriberException $e) {
						echo "<img src='img/false.png' width='200' height='170' /><br/><br/>";
						echo "<span style='font-size: 20px; color: red;'>"._("ERROR PROVISIONING SUBSCRIBER!")." </span><br/>".$e->getMessage()."<br/><br/><br/>";
						echo "<a href='provisioning.php'><button class='b1'>"._("Go Back")."</button></a>";
					}
					
					echo "</center>";
				} else {
					print_form(0,'');
				}

			?>

		</div>
	</body>
</html>
