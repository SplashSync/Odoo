<?php

/*
 *  This file is part of SplashSync Project.
 *
 *  Copyright (C) Splash Sync  <www.splashsync.com>
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
 *
 *  For the full copyright and license information, please view the LICENSE
 *  file that was distributed with this source code.
 */

namespace Splash\Local\Tests;

use Exception;
use Splash\Client\Splash;
use Splash\Tests\Tools\ObjectsCase;
use Splash\Models\Objects\Invoice\Status;

/**
 * Local Test Suite - Verify Writing of Invoices Status
 */
class L02InvoicesStatusTest extends ObjectsCase
{
    /**
     * @var array
     */
    private static $objectsIds = array();

    /**
     * @throws Exception
     *
     * @return void
     */
    public function testCreateObjects(): void
    {
        $this->createObject("Invoice", Status::DRAFT);
    }

    /**
     * Test Invoices Status
     *
     * @dataProvider statusProvider
     *
     * @param string $objectType
     * @param string $newStatus
     * @param string $expectedStatus
     * @param bool $withPayment
     *
     * @return void
     * @throws Exception
     */
    public function testStatusChanges(
        string $objectType,
        string $newStatus,
        string $expectedStatus,
        bool   $withPayment
    ): void {
        //====================================================================//
        //   Prepare Data for Update
        $newData = array("state" => $newStatus, "payments" => array());
        if ($withPayment) {
            //====================================================================//
            //   ADD Complete Payment Details
            $fields = $this->fakeFieldsList($objectType, array(), true);
            $fakeData = $this->fakeObjectData($fields);
            $newData["payments"] = array_replace_recursive($fakeData["payments"], array(
                "0" => array("amount" => 10.01),
                "1" => array("amount" => 10),
            ));
        }
        //====================================================================//
        //   Update Status Directly on Module
        Splash::object($objectType)->lock();
        $objectId = Splash::object($objectType)
            ->set(self::$objectsIds[$objectType], $newData)
        ;
        $this->assertNotEmpty($objectId);
        $this->assertEquals(self::$objectsIds[$objectType], $objectId);
        //====================================================================//
        //   Load Object
        $object = Splash::object($objectType)->get($objectId, $this->getReadFieldsList($objectType));
        $this->assertNotEmpty($object);
        //====================================================================//
        //   Check Status
        $this->assertEquals($expectedStatus, $object['state']);
        //====================================================================//
        //   Check Name
        $this->assertNotEmpty($object["name"]);
        $this->assertNotEquals("New", $object["name"]);
        //====================================================================//
        //   Check Payments
        $this->assertArrayHasKey("payments", $object);
        if ($withPayment) {
            $this->assertNotEmpty($object["payments"]);
        } else  {
            $this->assertEmpty($object["payments"]);
        }
    }

    /**
     * @throws Exception
     *
     * @return void
     */
    public function testStatusOnCreate(): void
    {
        $this->createObject("Invoice", Status::CANCELED);
        $this->createObject("Invoice", Status::DRAFT);
        $this->createObject("Invoice", Status::PAYMENT_DUE);
        $this->createObject("Invoice", Status::COMPLETE, true);
    }

    /**
     * @return array
     */
    public function statusProvider(): array
    {
        return array(
            //====================================================================//
            //   Tests For Invoice Objects
            "Inv: Draft   "     => array("Invoice",     Status::DRAFT,       Status::DRAFT,         false),
            "Inv: Cancel  "     => array("Invoice",     Status::CANCELED,    Status::CANCELED,      false),
            "Inv: Re Draft"     => array("Invoice",     Status::DRAFT,       Status::DRAFT,         false),
            "Inv: Valid   "     => array("Invoice",     Status::PAYMENT_DUE, Status::PAYMENT_DUE,   false),
            "Inv: Done    "     => array("Invoice",     Status::COMPLETE,    Status::COMPLETE,      true),
            "Inv: Partial "     => array("Invoice",     Status::COMPLETE,    Status::PAYMENT_DUE,   false),
            "Inv: Done 2  "     => array("Invoice",     Status::COMPLETE,    Status::COMPLETE,      true),
        );
    }

    /**
     * @param string $objectType
     * @param string $status
     * @param bool $withPayment
     *
     * @return array
     *
     * @throws Exception
     */
    private function createObject(string $objectType, string $status, bool $withPayment = false): array
    {
        //====================================================================//
        //   Create Fake Invoice Data
        $fields = $this->fakeFieldsList($objectType, array(), true, $withPayment);
        $fakeData = $this->fakeObjectData($fields);
        $fakeData["state"] = $status;
        //====================================================================//
        //   Force Items Qty & Prices
        $fakeData = array_replace_recursive($fakeData, array(
            "lines" => array(
                "0" => array("quantity" => 1, "discount" => 0, "price_unit" => array("ht" => 10, "ttc" => 10, "tax" => 0, "vat" => 0)),
                "1" => array("quantity" => 1, "discount" => 0, "price_unit" => array("ht" => 10, "ttc" => 10, "tax" => 0, "vat" => 0)),
            ),
            "payments" => array(
                "0" => array("amount" => 10),
                "1" => array("amount" => 10),
            )
        ));
        //====================================================================//
        //   Force Payments
        if ($withPayment) {
            $fakeData = array_replace_recursive($fakeData, array(
                "payments" => array(
                    "0" => array("amount" => 10),
                    "1" => array("amount" => 10),
                )
            ));
        }
        //====================================================================//
        //   Execute Action Directly on Module
        Splash::object($objectType)->lock();
        $objectId = Splash::object($objectType)->set(null, $fakeData);
        $this->assertNotEmpty($objectId);
        $this->assertIsString($objectId);
        //====================================================================//
        //   Add Object Id to Created List
        $this->addTestedObject($objectType, $objectId);
        self::$objectsIds[$objectType] = $objectId;
        //====================================================================//
        //   Load Object
        $object = Splash::object($objectType)->get($objectId, $this->getReadFieldsList($objectType));
        $this->assertNotEmpty($object);
        $this->assertEquals($status, $object["state"]);

        return $object;
    }

    /**
     * Get List of Fields to read
     *
     * @param string $objectType
     *
     * @return string[]
     *
     * @throws Exception
     */
    private function getReadFieldsList(string $objectType): array
    {
        return array_merge(
            $this->reduceFieldList($this->fakeFieldsList($objectType, array(), true), true),
            array("name"),
        );
    }
}
