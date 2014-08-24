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

?>
			<div id="stylized" class="myform">
				<form id="form" name="form" method="post" action="provisioning.php">
				<h1><?= _("Provision a new subscriber") ?></h1><br/>


				<span style='color: red; font-size: 12px;'><?= $errors ?></span><br/>
                                <label><?= _("Name") ?>
                                <span class="small"><?= _("Subscriber Name") ?></span>
                                </label>
                                <input type="text" name="firstname" id="firstname" value="<?=$firstname?>"/>

				<label><?= _("Subscriber number") ?>
				<span class="small"><?= _("Subscriber number") ?></span>
				</label>
				<input type="text" name="callerid" id="callerid" value="<?=$callerid?>"/>

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

					if ($firstname == "") {
						$error_txt .= _("Name is empty")."<br/>";
					}
					if ($callerid == "" || strlen($callerid) > 5 || strlen($callerid) < 5) {
						$error_txt .= _("Subscriber number is invalid")."<br/>";
					}
					if ($amount == "") {
						$error_txt .= _("Initial balance is empty")."<br/>";
					}
				} 

				if (isset($_POST['add_subscriber']) && $error_txt != "") {
					print_form(1,$error_txt);
				}elseif (isset($_POST['add_subscriber']) && $error_txt == "") {
					// no error process form
		                        
					$firstname = $_POST['firstname'];
                                        $callerid = $_POST['callerid'];
                                        $amount = $_POST['amount'];

					// get internal prefix
					$site = new Configuration();
					$info = $site->getSite();
					$internalprefix = $info->postcode.$info->pbxcode;

					$new_num = "$internalprefix$callerid";
				
					echo "<center>";
					
					$sub = new Subscriber();
					try {
						$sub->set("",$callerid,$firstname,1,$amount,"");
						$sub->create();
						echo "<img src='img/true.png' width='200' height='170' /><br/><br/>";
						echo "<span style='font-size: 20px;'>"._("Subscriber number").": <b>$callerid</b> "._("Successfully provisioned with an initial balance of")." $amount<br/><br/>";
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