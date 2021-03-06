<?php

require_once("httpful.phar");

class SMSException extends Exception { }

class SMS
{

	private $path = "http://localhost:8085/sms";

	public function send($source,$destination,$text) {
		$data = array("source" => $source, "destination" => $destination, "text" => $text);
		try {
			$response = \Httpful\Request::post($this->path."/send")->body($data)->sendsJson()->send();
		} catch (Httpful\Exception\ConnectionErrorException $e) {
			throw new SMSException($e->getMessage());
		}
		if ($response->code != 201) {
      throw new SMSException($response->body);
    }	
    $data = $response->body;
    if ($data->status == 'failed') {
            throw new SMSException(htmlentities($data->error));
    }
	}

        public function send_broadcast($text, $btype, $location) {
                $data = array("text" => $text, "btype" => $btype, "location" => $location);
                try {
                        $response = \Httpful\Request::post($this->path."/send_broadcast")->body($data)->sendsJson()->send();
                } catch (Httpful\Exception\ConnectionErrorException $e) {
                        throw new SMSException($e->getMessage());
                }

                $data = $response->body;
                if ($data->status == 'failed') {
                        throw new SMSException($data->error);
                }
                if ($data->status != 'success') {
                        throw new SMSException($data);
                }
        }


}


?>
